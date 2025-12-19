import pandas as pd
import os
from pathlib import Path
import argparse


def load_all_screen_pts_unified(path_log, end_hour=100, workflow_type='baseline', file_name_prefix='all_screeners'):
    """
    Consolidates individual daily simulation logs into master screener files.
    """
    columns = ['patient_id', 'patient_type', 'RSS', 'RSS_recall', 'dx_in_days', 'dx_slot_num', 'dx_at_day', 'recall_yn']

    if not os.path.exists(path_log):
        print(f"Error: Path not found - {path_log}")
        return

    # Iterate through batch directories (e.g., log_baseline_0, log_baseline_1)
    for daily_log_dir in os.listdir(path_log):
        sub_path = os.path.join(path_log, daily_log_dir)
        if not os.path.isdir(sub_path):
            continue

        print(f"Processing directory: {daily_log_dir}")
        pt_df_list = []

        for daily_file in os.listdir(sub_path):
            if not daily_file.endswith('.csv'):
                continue

            file_full_path = os.path.join(sub_path, daily_file)
            log_df = pd.read_csv(file_full_path)

            # 1. Filter for patients who completed the process
            complete_df = log_df[log_df.exit_system_ts < end_hour]

            # 2. Filter for screening patient types based on workflow
            if workflow_type == 'baseline':
                complete_df_screen = complete_df[complete_df.patient_type == 'screen']
            else:  # 1ss workflow
                screen_types = ['screen', 'screen + dx mammo us', 'screen + dx mammo', 'screen + dx us']
                complete_df_screen = complete_df[complete_df.patient_type.isin(screen_types)]

            if complete_df_screen.empty:
                continue

            # 3. Select columns and Extract Seed dynamically
            complete_df_screen = complete_df_screen[columns].copy()

            try:
                # Extracts the number between 'seed_' and '.csv' regardless of string length
                seed_str = daily_file.split('seed_')[-1].split('.csv')[0]
                complete_df_screen['seed'] = int(seed_str)
                pt_df_list.append(complete_df_screen)
            except (ValueError, IndexError):
                print(f"   Warning: Could not parse seed from filename: {daily_file}")

        # 4. Save the consolidated file for this batch
        if pt_df_list:
            final_pt_df = pd.concat(pt_df_list, ignore_index=True)

            # Extract batch number from directory name (the digit at the end)
            batch_id = daily_log_dir.split('_')[-1]
            out_file = f"./data/{file_name_prefix}_{batch_id}.csv"

            Path('./data').mkdir(parents=True, exist_ok=True)
            final_pt_df.to_csv(out_file, index=False)
            print(f"   Successfully saved: {out_file}")
        else:
            print(f"   No valid screening data found in {daily_log_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consolidate Clinic Simulation Logs")
    parser.add_argument('--workflow', type=str, choices=['no_1ss', '1ss'], required=True,
                        help="The workflow type to process")
    parser.add_argument('--end_hour', type=int, default=100,
                        help="Filter patients exiting before this hour")

    args = parser.parse_args()

    if args.workflow == 'no_1ss':
        load_all_screen_pts_unified(
            path_log='./output/output_temp_baseline/',
            end_hour=args.end_hour,
            workflow_type='baseline',
            file_name_prefix='all_screeners'
        )
    else:
        load_all_screen_pts_unified(
            path_log='./output/output_temp_1ss/',
            end_hour=args.end_hour,
            workflow_type='1ss',
            file_name_prefix='all_screeners_1ss'
        )


