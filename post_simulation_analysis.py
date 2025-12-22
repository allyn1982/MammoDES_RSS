import argparse
import os

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import ranksums, wilcoxon


def get_seed_num(filename):
    # This replaces the [36:-4] logic to be robust
    try:
        return int(filename.split('seed_')[-1].replace('.csv', ''))
    except:
        return None

def compare_pt_volumne_end_hour(path_log, path_log_smart, end_hour=10, type='baseline'):
    pt_vol_list, pt_vol_list_smart = [], []
    for daily_log in os.listdir(path_log):
        for daily_log_1 in os.listdir(path_log + daily_log):
            number = get_seed_num(daily_log_1)
            if number is not None and 393 >= number >= 29:
                log_df_baseline = pd.read_csv(path_log + daily_log + '/' + daily_log_1)
                complete_df_baseline = log_df_baseline[log_df_baseline.exit_system_ts < end_hour]
                pt_vol_list.append(complete_df_baseline.shape[0])

    for daily_log in os.listdir(path_log_smart):
        if not os.path.isdir(path_log_smart + daily_log): continue
        for daily_log_1 in os.listdir(path_log_smart + daily_log):
            number = get_seed_num(daily_log_1)
            if number is not None and 393 >= number >= 29:
                log_df_1ss = pd.read_csv(path_log_smart + daily_log + '/' + daily_log_1)
                complete_df_1ss = log_df_1ss[log_df_1ss.exit_system_ts < end_hour]
                pt_vol_list_smart.append(complete_df_1ss.shape[0])

    print(f'\n--- Volume Analysis ({type}) ---')
    print('Mean pts - no smart:', np.nanmean(pt_vol_list), 'sd:', np.nanstd(pt_vol_list))
    print('Mean pts - smart:', np.nanmean(pt_vol_list_smart), 'sd:', np.nanstd(pt_vol_list_smart))
    if len(pt_vol_list) == len(pt_vol_list_smart):
        print('Wilcoxon test:', wilcoxon(pt_vol_list, pt_vol_list_smart))
    return pt_vol_list, pt_vol_list_smart


def compare_waiting_time(path_log, path_log_smart, end_hour=10, type='baseline'):
    expected_exam_time_dict = {
        'screen': 0.467, 'dx mammo us': 1.687, 'dx mammo': 0.854, 'dx us': 0.854,
        'screen us': 0.55, 'mri': 0.05, 'mri-guided bx': 1.05, 'mammo bx': 2.237, 'us bx': 1.547,
        'screen + dx mammo us': 2.064, 'screen + dx mammo': 1.231, 'screen + dx us': 1.231
    }
    wait_time_list, wait_time_list_smart = [], []

    # Logic for No-Smart
    for daily_log in os.listdir(path_log):
        for daily_log_1 in os.listdir(path_log + daily_log):
            number = get_seed_num(daily_log_1)
            if number is not None and 393 >= number >= 29:
                log_df = pd.read_csv(path_log + daily_log + '/' + daily_log_1)
                complete_df = log_df[log_df.exit_system_ts < end_hour]
                for i in range(complete_df.shape[0]):
                    patient_type = complete_df.patient_type.to_list()[i]
                    los = complete_df.exit_system_ts.to_list()[i] - complete_df.arrival_ts.to_list()[i]
                    expected = expected_exam_time_dict[patient_type] + (
                        0.25 if type == '1ss' and patient_type == 'screen' else 0)
                    wait_time_list.append(los - expected)

    # Logic for Smart
    for daily_log in os.listdir(path_log_smart):
        if not os.path.isdir(path_log_smart + daily_log): continue
        for daily_log_1 in os.listdir(path_log_smart + daily_log):
            number = get_seed_num(daily_log_1)
            if number is not None and 393 >= number >= 29:
                log_df = pd.read_csv(path_log_smart + daily_log + '/' + daily_log_1)
                complete_df = log_df[log_df.exit_system_ts < end_hour]
                for i in range(complete_df.shape[0]):
                    patient_type = complete_df.patient_type.to_list()[i]
                    los = complete_df.exit_system_ts.to_list()[i] - complete_df.arrival_ts.to_list()[i]
                    expected = expected_exam_time_dict[patient_type] + (
                        0.25 if type == '1ss' and patient_type == 'screen' else 0)
                    wait_time_list_smart.append(los - expected)

    print(f'\n--- Waiting Time Analysis ({type}) ---')
    print('Avg wait - no smart:', np.nanmean(wait_time_list))
    print('Avg wait - smart:', np.nanmean(wait_time_list_smart))
    print('Ranksums test:', ranksums(wait_time_list, wait_time_list_smart))
    return wait_time_list, wait_time_list_smart


def RSS_analysis(path_log, end_hour=100, type='baseline'):
    rss_list, rss_recall_list = [], []
    for daily_log in os.listdir(path_log):
        for daily_log_1 in os.listdir(path_log + daily_log):
            number = get_seed_num(daily_log_1)
            if number is not None and 393 >= number >= 29:
                log_df = pd.read_csv(path_log + daily_log + '/' + daily_log_1)
                complete_df = log_df[log_df.exit_system_ts < end_hour]
                if type == 'baseline':
                    screen_df = complete_df[complete_df.patient_type == 'screen']
                else:
                    screen_df = complete_df[complete_df.patient_type.isin(
                        ['screen', 'screen + dx mammo', 'screen + dx mammo us', 'screen + dx us'])]

                rss_list.append(screen_df.shape[0])
                rss_recall_list.append(screen_df[screen_df.RSS_recall == 'Yes'].shape[0])

    print(f'\n--- RSS Analysis ({type}) ---')
    print('% recall overall:', sum(rss_recall_list) / sum(rss_list) if sum(rss_list) > 0 else 0)
    print('Variance of recalls:', np.var(rss_recall_list))
    return rss_recall_list

def compare_operating_time(path_log, path_log_smart, end_hour=100, type='baseline'):
    op_time_list, op_time_list_smart = [], []
    for daily_log in os.listdir(path_log):
        for daily_log_1 in os.listdir(path_log+daily_log):
            number = get_seed_num(daily_log_1)
            if 393 >= number >= 29:
                log_df_baseline = pd.read_csv(path_log + daily_log + '/' + daily_log_1)
                complete_df_baseline = log_df_baseline[log_df_baseline.exit_system_ts < end_hour]
                op_time_list.append(max(complete_df_baseline.exit_system_ts.to_list()))
    for daily_log in os.listdir(path_log_smart):
        for daily_log_1 in os.listdir(path_log + daily_log):
            number = get_seed_num(daily_log_1)
            if 393 >= number >= 29:
                log_df_1ss = pd.read_csv(path_log_smart + daily_log + '/' + daily_log_1)
                complete_df_1ss = log_df_1ss[log_df_1ss.exit_system_ts < end_hour]
                op_time_list_smart.append(max(complete_df_1ss.exit_system_ts.to_list()))

    print(f'\n--- Operating Hours Analysis ({type}) ---')
    print('Ave operating time in hours - no smart: ', np.nanmean(op_time_list),
          ', sd: ', np.nanstd(op_time_list))
    print('Ave operating time in hours - smart: ', np.nanmean(op_time_list_smart),
          ', sd: ', np.nanstd(op_time_list_smart))

    print('Wilcoxon test: ', wilcoxon(op_time_list, op_time_list_smart))



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--workflow', choices=['baseline', '1ss'], required=True)
    parser.add_argument('--analysis', choices=['volume', 'waiting', 'hours', 'rss', 'all'], default='all')
    args = parser.parse_args()

    # Paths
    path_base = f'./output/output_temp_{args.workflow}/'
    path_smart = f'./output/output_temp_{args.workflow}_smart/'

    if args.analysis in ['volume', 'all']:
        compare_pt_volumne_end_hour(path_base, path_smart, end_hour=10, type=args.workflow)

    if args.analysis in ['waiting', 'all']:
        compare_waiting_time(path_base, path_smart, end_hour=10, type=args.workflow)

    if args.analysis in ['hours', 'all']:
        compare_operating_time(path_base, path_smart, end_hour=100, type=args.workflow)

    if args.analysis in ['rss', 'all']:
        print("Running RSS for No-Smart...")
        r_no = RSS_analysis(path_base, type=args.workflow)
        print("Running RSS for Smart...")
        r_smart = RSS_analysis(path_smart, type=args.workflow)
        print("\nLevene Test (Variance):", stats.levene(r_no, r_smart))
        print('-------------------------------------------------------------')
