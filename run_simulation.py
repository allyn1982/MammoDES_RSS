import pandas as pd
import numpy as np
import simpy
import math
import random
import argparse
from pathlib import Path
from numpy.random import default_rng

from clinic_wf_1ss import get_exam_1ss
from clinic_wf_no_1ss import get_exam
from resources import MammoClinic_1SS, MammoClinic
from create_screener_pool import load_all_screen_pts_unified
from utils import compute_durations_baseline, compute_durations_1ss


def run_clinic_unified(env, clinic, rg, pt_num_list, acc_pt_num_list, pt_num_total,
                       rss_params, smart, i, is_1ss, additional_1ss_params=None,
                       stoptime=None, max_arrivals=simpy.core.Infinity, dx_info_dict=None):
    patient = 0
    cur_hour = math.floor(env.now)
    rss_1, rss_2, rss_3, rss_1_recall, rss_2_recall, rss_3_recall = rss_params

    while env.now < stoptime and patient < max_arrivals:
        patient_num_at_current_hour = pt_num_list[cur_hour]
        mean_interarrival_time = 1.0 / patient_num_at_current_hour
        iat = rg.exponential(mean_interarrival_time)

        if cur_hour == math.floor(env.now):
            yield env.timeout(iat)

        if env.now > stoptime:
            break

        patient += 1
        recall_dx = (i in dx_info_dict and patient in dx_info_dict[i])

        if not is_1ss:
            env.process(get_exam(env, patient, clinic, rg, pt_num_total, recall_dx,
                                 rss_1, rss_2, rss_3, rss_1_recall, rss_2_recall, rss_3_recall,
                                 smart, num_days_8_rss_3, avg_num_rss_3, all_screener_df, i))
        else:
            avg_recall_rate, ai_on_dict, rad_change, rad_change_2, agreement_rss_same_day_ai = additional_1ss_params
            env.process(get_exam_1ss(
                env, patient, clinic, rg, pt_num_total, avg_recall_rate, ai_on_dict, rad_change, rad_change_2,
                rss_1, rss_2, rss_3, rss_1_recall, rss_2_recall, rss_3_recall, recall_dx, smart,
                agreement_rss_same_day_ai,
                num_days_8_rss_3, avg_num_rss_3, all_screener_df, patient_screener_count, i
            ))

        if math.floor(env.now) == cur_hour and patient >= acc_pt_num_list[cur_hour]:
            yield env.timeout(cur_hour + 1 - env.now)
            cur_hour += 1
        elif math.floor(env.now) > cur_hour and patient >= acc_pt_num_list[cur_hour]:
            cur_hour = math.floor(env.now)


def main_simulation(i, j, is_1ss, iterations, dx_info_dict, smart, rss_params, clinic_cfg, rg):
    # rg = default_rng(i + j +5)

    # Load arrival data
    num_pt_per_hour = pd.read_csv('./data/num_pt_per_hour.csv')
    pt_num_list = list(num_pt_per_hour.avg)
    pt_num_list[-1] *= 2
    pt_num_total = int(sum(pt_num_list))
    acc_pt_num_list = np.cumsum(pt_num_list).tolist()

    env = simpy.Environment()
    stoptime = clinic_cfg.pop('stoptime')  # Remove to pass remaining dict to Clinic class

    if not is_1ss:
        clinic = MammoClinic(env, **clinic_cfg, rg=rg)
        add_params = None
        folder = "output_temp_baseline" + ("_smart" if smart else "")
        prefix = "baseline"
    else:
        ai_on_dict = {h: True for h in range(7, 17)}
        avg_recall_rate = (rss_params[0] * rss_params[3]) + (rss_params[1] * rss_params[4]) + (
                    rss_params[2] * rss_params[5])
        add_params = (avg_recall_rate, ai_on_dict, False, False, False)

        clinic = MammoClinic_1SS(env, **clinic_cfg, num_radiologist_same_day=0,
                                 rad_change=False, rad_change_2=False, rg=rg)
        folder = "output_temp_1ss" + ("_smart" if smart else "")
        prefix = "1ss"

    out_path = f"./output/{folder}/log_{prefix}_{j}"
    Path(out_path).mkdir(parents=True, exist_ok=True)

    env.process(run_clinic_unified(env, clinic, rg, pt_num_list, acc_pt_num_list, pt_num_total,
                                   rss_params, smart, i, is_1ss, add_params, stoptime, dx_info_dict=dx_info_dict))
    env.run()

    df = pd.DataFrame(clinic.timestamps_list)
    file_path = f"{out_path}/clinic_log_{prefix}_seed_{i}.csv"
    df.to_csv(file_path, index=False)
    return file_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clinic Simulation Suite")

    # Workflow & Iterations
    parser.add_argument('--is_1ss', type=str, choices=['yes', 'no'], required=True)
    parser.add_argument('--iterations', type=int, default=500)
    parser.add_argument('--smart', action='store_true')

    # RSS & Recall Parameters
    parser.add_argument('--rss1', type=float, default=0.44)
    parser.add_argument('--rss2', type=float, default=0.28)
    parser.add_argument('--rss3', type=float, default=0.28)
    parser.add_argument('--r1_recall', type=float, default=0.06)
    parser.add_argument('--r2_recall', type=float, default=0.12)
    parser.add_argument('--r3_recall', type=float, default=0.18)

    # Clinic Resource Variables
    parser.add_argument('--num_checkin', type=int, default=3)
    parser.add_argument('--num_wait_pub', type=int, default=20)
    parser.add_argument('--num_consent', type=int, default=2)
    parser.add_argument('--num_change', type=int, default=3)
    parser.add_argument('--num_wait_gown', type=int, default=5)
    parser.add_argument('--num_scanner', type=int, default=3)
    parser.add_argument('--num_us', type=int, default=2)
    parser.add_argument('--num_rad', type=int, default=4)
    parser.add_argument('--stoptime', type=float, default=9.5)

    args = parser.parse_args()

    # Organize parameters
    is_1ss_bool = (args.is_1ss == 'yes')
    rss_params = (args.rss1, args.rss2, args.rss3, args.r1_recall, args.r2_recall, args.r3_recall)

    # Map CLI args to internal clinic class expectations
    clinic_cfg = {
        "num_checkin_staff": args.num_checkin,
        "num_public_wait_room": args.num_wait_pub,
        "num_consent_staff": args.num_consent,
        "num_change_room": args.num_change,
        "num_gowned_wait_room": args.num_wait_gown,
        "num_scanner": args.num_scanner,
        "num_us_machine": args.num_us,
        "num_radiologist": args.num_rad,
        "stoptime": args.stoptime
    }

    seed_list = [42, 1234, 2024, 0, 999]

    for j, seed in enumerate(seed_list):
        random.seed(seed)
        dx_info_dict = {}

        if args.smart:
            csv_suffix = "1ss_" if is_1ss_bool else "baseline_"
            all_screener_df = pd.read_csv(f'./data/all_screeners_{csv_suffix}{j}.csv')
            for key, group in all_screener_df.groupby('dx_at_day'):
                dx_info_dict[key] = group['dx_slot_num'].tolist()
            num_days_8_rss_3 = all_screener_df.RSS.to_list().count(3) % args.iterations
            avg_num_rss_3 = int(all_screener_df.RSS.to_list().count(3) / args.iterations)
        else:
            all_screener_df = pd.DataFrame(columns=['patient_id', 'patient_type', 'RSS', 'RSS_recall', 'dx_in_days',
                                                    'dx_at_day', 'recall_yn', 'dx_slot_num', 'seed'])
            num_days_8_rss_3 = 0
            avg_num_rss_3 = 0

        rg = default_rng(seed=seed)

        for i in range(args.iterations):
            patient_screener_count = 0
            try:
                path = main_simulation(i, j, is_1ss_bool, args.iterations, dx_info_dict, args.smart, rss_params,
                                       clinic_cfg.copy(), rg)

                log_df = pd.read_csv(path)
                log_df = compute_durations_1ss(log_df) if is_1ss_bool else compute_durations_baseline(log_df)
                log_df.to_csv(path, index=False)
            except Exception as e:
                print(f"Error in Seed {seed} Iter {i}: {e}")

        print(f"Completed Batch for Seed {seed}")


    if not args.smart:
        print("\n--- Simulation Complete. Running Screener Pool Consolidation ---")

        folder_type = "1ss" if is_1ss_bool else "baseline"
        path_to_logs = f'./output/output_temp_{folder_type}/'

        workflow_label = "1ss" if is_1ss_bool else "baseline"

        load_all_screen_pts_unified(
            path_log=path_to_logs,
            end_hour=100,
            workflow_type=workflow_label,
            file_name_prefix=f'all_screeners_{workflow_label}'
        )
    else:
        print("\n--- Simulation Complete. Smart=False → skipping screener pool generation ---")