import math
import random

import pandas as pd

from params import exam_type_prob, screener_type_1ss

def get_exam_1ss(env, patient, clinic, rg, pt_num_total, avg_recall_rate, ai_on_dict, rad_change, rad_change_2,
              rss_1, rss_2, rss_3, rss_1_recall, rss_2_recall, rss_3_recall, recall_dx, smart, agreement_rss_same_day_ai,
                 num_days_8_rss_3, avg_num_rss_3, all_screener_df, patient_screener_count, i):
    day = i
    if clinic.current_day != day:
        clinic.current_day = day
        clinic.daily_screener_count = 0

    # patient arrives to clinic
    arrival_ts = env.now

    # generate a random number
    number = rg.random()

    # define log vars
    patient_type = ""
    got_checkin_staff_ts, release_checkin_staff_ts, got_change_room_ts, release_change_room_ts = pd.NA, pd.NA, pd.NA, pd.NA
    got_public_wait_room_ts, release_public_wait_room_ts, got_consent_staff_ts, release_consent_staff_ts = pd.NA, pd.NA, pd.NA, pd.NA
    got_gowned_wait_room_ts, release_gowned_wait_room_ts, got_screen_scanner_ts, release_screen_scanner_ts = pd.NA, pd.NA, pd.NA, pd.NA
    got_dx_scanner_after_ai_ts, release_dx_scanner_after_ai_ts, got_us_machine_after_ai_ts, release_us_machine_after_ai_ts = pd.NA, pd.NA, pd.NA, pd.NA
    got_dx_scanner_before_us_after_ai_ts, release_dx_scanner_before_us_after_ai_ts, got_us_machine_after_dx_scanner_after_ai_ts, release_dx_scanner_us_machine_after_ai_ts = pd.NA, pd.NA, pd.NA, pd.NA
    begin_ai_assess_ts, end_ai_assess_ts, got_dx_scanner_ts, release_dx_scanner_ts = pd.NA, pd.NA, pd.NA, pd.NA
    got_us_machine_ts, release_us_machine_ts, got_dx_scanner_before_us_ts, release_dx_scanner_before_us_ts = pd.NA, pd.NA, pd.NA, pd.NA
    got_us_machine_after_dx_scanner_ts, release_dx_scanner_us_machine_ts, got_us_machine_bx_ts, release_us_machine_after_bx_ts = pd.NA, pd.NA, pd.NA, pd.NA
    got_scanner_bx_ts, got_scanner_after_us_bx_ts, release_scanner_after_post_bx_mammo_ts, got_screen_us_machine_ts = pd.NA, pd.NA, pd.NA, pd.NA
    release_screen_us_machine_ts, got_scanner_after_mri_bx_ts, got_mri_machine_ts, release_mri_machine_ts = pd.NA, pd.NA, pd.NA, pd.NA
    got_checkout_change_room_ts, release_checkout_change_room_ts, get_rad_dx_mammo_ts, release_rad_dx_mammo_ts = pd.NA, pd.NA, pd.NA, pd.NA
    get_rad_dx_us_ts, release_rad_dx_us_ts, get_rad_dx_mammo_us_mammo_ts, release_rad_dx_mammo_us_mammo_ts = pd.NA, pd.NA, pd.NA, pd.NA
    get_rad_dx_mammo_us_us_ts, release_rad_dx_mammo_us_us_ts, get_rad_ux_bx_ts, release_rad_us_bx_ts = pd.NA, pd.NA, pd.NA, pd.NA
    get_rad_mri_bx_ts, release_rad_mri_bx_ts, get_rad_mammo_bx_ts, release_rad_mammo_bx_ts = pd.NA, pd.NA, pd.NA, pd.NA
    get_rad_dx_mammo_us_mammo_after_ai_ts, release_rad_dx_mammo_us_mammo_after_ai_ts, get_rad_dx_mammo_us_us_after_ai_ts, release_rad_dx_mammo_us_us_after_ai_ts = pd.NA, pd.NA, pd.NA, pd.NA
    get_rad_dx_mammo_after_ai_ts, release_rad_dx_mammo_after_ai_ts, get_rad_dx_us_after_ai_ts, release_rad_dx_us_after_ai_ts = pd.NA, pd.NA, pd.NA, pd.NA
    RSS, RSS_recall = pd.NA, pd.NA
    dx_in_days, dx_slot_num, dx_at_day = pd.NA, pd.NA, pd.NA
    exit_system_ts = pd.NA

    # get exam type distribution based on current time
    exam_type_distribution = exam_type_prob(arrival_ts)

    pct_screen_mammo_scheduled_baseline = list(exam_type_distribution.values())[0]
    pct_dx_mammo_us_scheduled_baseline = sum(list(exam_type_distribution.values())[:2])
    pct_dx_mammo_scheduled_baseline = sum(list(exam_type_distribution.values())[:3])
    pct_dx_us_scheduled_baseline = sum(list(exam_type_distribution.values())[:4])
    pct_us_guided_bx_scheduled_baseline = sum(list(exam_type_distribution.values())[:5])
    pct_mammo_guided_bx_scheduled_baseline = sum(list(exam_type_distribution.values())[:6])
    pct_screen_us_scheduled_baseline = sum(list(exam_type_distribution.values())[:7])
    pct_mri_guided_bx_scheduled_baseline = sum(list(exam_type_distribution.values())[:8])

    # initialize all scheduled percentages to baseline
    pct_screen_mammo_scheduled = pct_screen_mammo_scheduled_baseline
    pct_dx_mammo_us_scheduled = pct_dx_mammo_us_scheduled_baseline
    pct_dx_mammo_scheduled = pct_dx_mammo_scheduled_baseline
    pct_dx_us_scheduled = pct_dx_us_scheduled_baseline
    pct_us_guided_bx_scheduled = pct_us_guided_bx_scheduled_baseline
    pct_mammo_guided_bx_scheduled = pct_mammo_guided_bx_scheduled_baseline
    pct_screen_us_scheduled = pct_screen_us_scheduled_baseline
    pct_mri_guided_bx_scheduled = pct_mri_guided_bx_scheduled_baseline

    # apply AI-specific adjustments
    ai = ai_on_dict[math.floor(arrival_ts) + 7]
    pct_screen_mammo_after_ai_us_scheduled = pct_screen_mammo_scheduled

    # if a dx recall has been taken care of same day as the screen mammo
    if recall_dx:
        recall_yn = 'Yes'
    else:
        recall_yn = 'No'

    # determine no show
    number_no_show = rg.random()

    if number_no_show > 0.1: # skip already performed same-day dx recall
        no_show = 'No'

        # request a checkin staff
        with clinic.checkin_staff.request() as request:
            yield request
            got_checkin_staff_ts = env.now
            yield env.process(clinic.pt_checkin(patient))
            release_checkin_staff_ts = env.now

        # mri has own change rooms
        if number > pct_screen_us_scheduled:
            # 11. mri-guided bx
            if pct_screen_us_scheduled < number <= pct_mri_guided_bx_scheduled:
                patient_type = 'mri-guided bx'
                with clinic.radiologist.request() as request_rad:
                    yield request_rad
                    got_mri_machine_ts = env.now
                    yield env.process(clinic.get_mri_guided_bx(patient))
                    release_mri_machine_ts = env.now

                # post bx mammo
                request = clinic.scanner.request()
                yield request
                got_scanner_after_mri_bx_ts = env.now
                yield env.process(clinic.get_dx_mammo(patient))

                # rad review
                request_rad_2 = clinic.radiologist.request()
                yield request_rad_2
                get_rad_mri_bx_ts = env.now
                yield env.process(clinic.rad_review(patient))
                clinic.scanner.release(request)
                clinic.radiologist.release(request_rad_2)
                release_rad_mri_bx_ts = env.now
                release_scanner_after_post_bx_mammo_ts = env.now

            # Other mri procedures
            if number > pct_mri_guided_bx_scheduled:
                patient_type = 'mri'

        else:
            # request a public wait room
            with clinic.public_wait_room.request() as request:
                yield request
                got_public_wait_room_ts = env.now
                yield env.process(clinic.use_public_wait_room(patient))
                release_public_wait_room_ts = env.now

            # request consent room (bx only)
            if number > pct_dx_us_scheduled:
                with clinic.consent_staff.request() as request:
                    yield request
                    got_consent_staff_ts = env.now
                    yield env.process(clinic.consent_patient(patient))
                    release_consent_staff_ts = env.now
            else:
                got_consent_staff_ts = pd.NA
                release_consent_staff_ts = pd.NA

            # request change room
            with clinic.change_room.request() as request:
                yield request
                got_change_room_ts = env.now
                yield env.process(clinic.use_change_room(patient))
                release_change_room_ts = env.now

            # request gowned wait room
            with clinic.gowned_wait_room.request() as request:
                yield request
                got_gowned_wait_room_ts = env.now
                yield env.process(clinic.use_gowned_wait_room((patient)))
                release_gowned_wait_room_ts = env.now

            # 1-4. screen mammo w/ or w/o same-day dx
            if number <= pct_screen_mammo_after_ai_us_scheduled:

                clinic.daily_screener_count += 1
                count = clinic.daily_screener_count

                if not smart: # random draw from screener pool
                    # determine RSS
                    number_RSS = rg.random()
                    if number_RSS <= rss_1:
                        RSS = 1
                    elif rss_1 + rss_2 >= number_RSS > rss_1:
                        RSS = 2
                    else:
                        RSS = 3

                    # determine recall
                    type_number = rg.random()
                    number_RSS_recall = rg.random()
                    if agreement_rss_same_day_ai: # sensitivity analysis
                        rss_1_recall = rss_1_recall*0.9 # same-day ai 90% agree w/ rss
                        rss_2_recall = rss_2_recall*0.9
                        rss_3_recall = rss_3_recall*0.9

                    if RSS == 1 and number_RSS_recall <= rss_1_recall:
                        RSS_recall = 'Yes'
                        # secure a future slot for dx
                        dx_in_days = int(rg.normal(20, 4))
                        dx_slot_num = random.randint(1, int(
                            pt_num_total * 0.67))  # pt_num_total*0.67 is to avoid dx img too late in a day
                        dx_at_day = dx_in_days + i
                        patient_type = screener_type_1ss(type_number)
                    elif RSS == 1 and number_RSS_recall > rss_1_recall:
                        RSS_recall = 'No'
                        dx_in_days, dx_slot_num, dx_at_day = pd.NA, pd.NA, pd.NA
                        patient_type = 'screen'
                    elif RSS == 2 and number_RSS_recall <= rss_2_recall:
                        RSS_recall = 'Yes'
                        # secure a future slot for dx
                        dx_in_days = int(rg.normal(20, 4))
                        dx_slot_num = random.randint(1, int(pt_num_total * 0.67))
                        dx_at_day = dx_in_days + i
                        patient_type = screener_type_1ss(type_number)
                    elif RSS == 2 and number_RSS_recall > rss_2_recall:
                        RSS_recall = 'No'
                        dx_in_days, dx_slot_num, dx_at_day = pd.NA, pd.NA, pd.NA
                        patient_type = 'screen'
                    elif RSS == 3 and number_RSS_recall <= rss_3_recall:
                        RSS_recall = 'Yes'
                        # secure a future slot for dx
                        dx_in_days = int(rg.normal(20, 4))
                        dx_slot_num = random.randint(1, int(pt_num_total * 0.67))
                        dx_at_day = dx_in_days + i
                        patient_type = screener_type_1ss(type_number)
                    elif RSS == 3 and number_RSS_recall > rss_3_recall:
                        RSS_recall = 'No'
                        dx_in_days, dx_slot_num, dx_at_day = pd.NA, pd.NA, pd.NA
                        patient_type = 'screen'
                else:  # smart
                    # determine number of RSS 3 and RSS 2 patients for the day
                    if i <= num_days_8_rss_3:
                        num_rss_3_per_day = avg_num_rss_3 + 1
                        num_rss_2_per_day = avg_num_rss_3 + 1
                    else:
                        num_rss_3_per_day = avg_num_rss_3
                        num_rss_2_per_day = avg_num_rss_3

                    # determine which RSS group to sample from based on daily count
                    if count <= num_rss_3_per_day:
                        candidate_df = all_screener_df[all_screener_df.RSS == 3]
                    elif count <= num_rss_3_per_day + num_rss_2_per_day:
                        candidate_df = all_screener_df[all_screener_df.RSS == 2]
                    else:
                        candidate_df = all_screener_df[all_screener_df.RSS == 1]

                    # fallback: if no candidates in preferred RSS group, sample from remaining screeners
                    if candidate_df.empty:
                        candidate_df = all_screener_df

                    # sample one patient and remove from the pool
                    sampled_row = candidate_df.sample(n=1, replace=False)
                    RSS = sampled_row.RSS.iloc[0]
                    RSS_recall = sampled_row.RSS_recall.iloc[0]
                    dx_in_days = sampled_row.dx_in_days.iloc[0]
                    dx_slot_num = sampled_row.dx_slot_num.iloc[0]
                    dx_at_day = sampled_row.dx_at_day.iloc[0]
                    patient_type = sampled_row.patient_type.iloc[0]

                    all_screener_df.drop(index=sampled_row.index, inplace=True)

                # all screeners need screen mammo
                with clinic.scanner.request() as request:
                    yield request
                    got_screen_scanner_ts = env.now
                    yield env.process(clinic.get_screen_mammo(patient))
                    release_screen_scanner_ts = env.now

                if ai:
                    # AI assessment
                    if rad_change:
                        request_rad_ai = clinic.radiologist_same_day.request()
                    else:
                        request_rad_ai = clinic.radiologist.request()
                    yield request_rad_ai
                    # print('1 - Same day rad doing review after screen mammo at', env.now)
                    begin_ai_assess_ts = env.now
                    yield env.process(clinic.get_ai_assess(patient))
                    end_ai_assess_ts = env.now
                    if rad_change:
                        clinic.radiologist_same_day.release(request_rad_ai)
                    else:
                        clinic.radiologist.release(request_rad_ai)
                    # print('1 - Same day rad finished doing review after screen mammo at', env.now)

                if patient_type == 'screen + dx mammo us' and ai:
                    # dx mammo
                    request_2 = clinic.scanner.request()
                    yield request_2
                    got_dx_scanner_before_us_after_ai_ts = env.now
                    yield env.process(clinic.get_dx_mammo(patient))

                    # rad review
                    if rad_change:
                        request_rad_after_ai = clinic.radiologist_same_day.request()
                    else:
                        request_rad_after_ai = clinic.radiologist.request()
                    yield request_rad_after_ai
                    # print('2 - Same day rad doing review dx mammo after screen at', env.now)

                    get_rad_dx_mammo_us_mammo_after_ai_ts = env.now
                    yield env.process(clinic.rad_review(patient))
                    clinic.scanner.release(request_2)
                    if rad_change:
                        clinic.radiologist_same_day.release(request_rad_after_ai)
                    else:
                        clinic.radiologist.release(request_rad_after_ai)
                    release_dx_scanner_before_us_after_ai_ts = env.now
                    release_rad_dx_mammo_us_mammo_after_ai_ts = env.now
                    # print('2 - Same day rad done doing review dx mammo after screen at ', env.now)

                    # dx us
                    request_3 = clinic.us_machine.request()
                    yield request_3
                    got_us_machine_after_dx_scanner_after_ai_ts = env.now
                    yield env.process(clinic.get_dx_us(patient))
                    # rad review
                    if rad_change:
                        request_rad_after_ai_2 = clinic.radiologist_same_day.request()
                    else:
                        request_rad_after_ai_2 = clinic.radiologist.request()
                    yield request_rad_after_ai_2
                    # print('2 - Same day rad doing review dx us after screen at', env.now)

                    get_rad_dx_mammo_us_us_after_ai_ts = env.now
                    yield env.process(clinic.rad_review(patient))
                    clinic.us_machine.release(request_3)
                    if rad_change:
                        clinic.radiologist_same_day.release(request_rad_after_ai_2)
                    else:
                        clinic.radiologist.release(request_rad_after_ai_2)
                    release_dx_scanner_us_machine_after_ai_ts = env.now
                    release_rad_dx_mammo_us_us_after_ai_ts = env.now
                    # print('2 - Same day rad done doing review dx us after screen at', env.now)

                elif patient_type == 'screen + dx mammo' and ai:
                    # dx mammo
                    request_2 = clinic.scanner.request()
                    yield request_2
                    got_dx_scanner_after_ai_ts = env.now
                    yield env.process(clinic.get_dx_mammo(patient))

                    # rad review
                    if rad_change:
                        request_rad_after_ai = clinic.radiologist_same_day.request()
                    else:
                        request_rad_after_ai = clinic.radiologist.request()
                    yield request_rad_after_ai
                    # print('3 - Same day rad doing review for dx mammo after screen at', env.now)

                    get_rad_dx_mammo_after_ai_ts = env.now
                    yield env.process(clinic.rad_review(patient))
                    clinic.scanner.release(request_2)
                    if rad_change:
                        clinic.radiologist_same_day.release(request_rad_after_ai)
                    else:
                        clinic.radiologist.release(request_rad_after_ai)
                    release_rad_dx_mammo_after_ai_ts = env.now
                    release_dx_scanner_after_ai_ts = env.now
                    # print('3 - Same day rad done doing review for dx mammo after screen at', env.now)

                elif patient_type == 'screen + dx us' and ai:
                    # dx us
                    request_2 = clinic.us_machine.request()
                    yield request_2
                    got_us_machine_after_ai_ts = env.now
                    yield env.process(clinic.get_dx_us(patient))

                    # rad review
                    if rad_change:
                        request_rad_after_ai = clinic.radiologist_same_day.request()
                    else:
                        request_rad_after_ai = clinic.radiologist.request()
                    yield request_rad_after_ai
                    # print('3 - Same day rad doing review for dx us after screen at', env.now)

                    get_rad_dx_us_after_ai_ts = env.now
                    yield env.process(clinic.rad_review(patient))
                    clinic.us_machine.release(request_2)
                    if rad_change:
                        clinic.radiologist_same_day.release(request_rad_after_ai)
                    else:
                        clinic.radiologist.release(request_rad_after_ai)
                    release_rad_dx_us_after_ai_ts = env.now
                    release_us_machine_after_ai_ts = env.now
                    # print('3 - Same day rad done doing review for dx us after screen at', env.now)

            # 5. dx mammo + dx us
            if pct_screen_mammo_after_ai_us_scheduled < number <= pct_dx_mammo_us_scheduled:
                patient_type = 'dx mammo us'
                request = clinic.scanner.request()
                yield request
                got_dx_scanner_before_us_ts = env.now
                yield env.process(clinic.get_dx_mammo(patient))

                # rad review
                if rad_change_2:
                    if clinic.radiologist_same_day.count != 0:  # count how many being used, if used then request radiologist
                        request_rad = clinic.radiologist.request()
                        yield request_rad
                        get_rad_dx_mammo_us_mammo_ts = env.now
                        yield env.process(clinic.rad_review(patient))
                        clinic.scanner.release(request)
                        clinic.radiologist.release(request_rad)
                    else:
                        request_rad_2 = clinic.radiologist_same_day.request()
                        yield request_rad_2
                        # print('5 - Same day rad doing review for dx mammo at', env.now)
                        get_rad_dx_mammo_us_mammo_ts = env.now
                        yield env.process(clinic.rad_review(patient))
                        clinic.scanner.release(request)
                        clinic.radiologist_same_day.release(request_rad_2)
                        # print('5 - Same day rad done doing review for dx mammo at', env.now)
                else:
                    request_rad = clinic.radiologist.request()
                    yield request_rad
                    get_rad_dx_mammo_us_mammo_ts = env.now
                    yield env.process(clinic.rad_review(patient))
                    clinic.scanner.release(request)
                    clinic.radiologist.release(request_rad)
                release_rad_dx_mammo_us_mammo_ts = env.now
                release_dx_scanner_before_us_ts = env.now

                # dx us
                request_2 = clinic.us_machine.request()
                yield request_2
                got_us_machine_after_dx_scanner_ts = env.now
                yield env.process(clinic.get_dx_us(patient))

                # rad review
                if rad_change_2:
                    if clinic.radiologist_same_day.count != 0:
                        request_rad_4 = clinic.radiologist.request()
                        yield request_rad_4
                        get_rad_dx_mammo_us_us_ts = env.now
                        yield env.process(clinic.rad_review(patient))
                        clinic.us_machine.release(request_2)
                        clinic.radiologist.release(request_rad_4)
                    else:
                        request_rad_3 = clinic.radiologist_same_day.request()
                        yield request_rad_3
                        # print('5 - Same day rad doing review for dx us at', env.now)
                        get_rad_dx_mammo_us_us_ts = env.now
                        yield env.process(clinic.rad_review(patient))
                        clinic.us_machine.release(request_2)
                        clinic.radiologist_same_day.release(request_rad_3)
                        # print('5 - Same day rad done doing review for dx us at', env.now)

                else:
                    request_rad_4 = clinic.radiologist.request()
                    yield request_rad_4
                    get_rad_dx_mammo_us_us_ts = env.now
                    yield env.process(clinic.rad_review(patient))
                    clinic.us_machine.release(request_2)
                    clinic.radiologist.release(request_rad_4)
                release_rad_dx_mammo_us_us_ts = env.now
                release_dx_scanner_us_machine_ts = env.now

            # 6. dx mammo
            if pct_dx_mammo_us_scheduled < number <= pct_dx_mammo_scheduled:
                patient_type = 'dx mammo'
                request = clinic.scanner.request()
                yield request
                got_dx_scanner_ts = env.now
                yield env.process(clinic.get_dx_mammo(patient))
                # rad review
                if rad_change_2:
                    if clinic.radiologist_same_day.count != 0:
                        request_rad = clinic.radiologist.request()
                        yield request_rad
                        get_rad_dx_mammo_ts = env.now
                        yield env.process(clinic.rad_review(patient))
                        clinic.scanner.release(request)
                        clinic.radiologist.release(request_rad)
                    else:
                        request_rad_2 = clinic.radiologist_same_day.request()
                        yield request_rad_2
                        # print('6 - Same day rad doing review for dx mammo at', env.now)
                        get_rad_dx_mammo_ts = env.now
                        yield env.process(clinic.rad_review(patient))
                        clinic.scanner.release(request)
                        clinic.radiologist_same_day.release(request_rad_2)
                        # print('6 - Same day rad done doing review for dx mammo at', env.now)

                else:
                    request_rad = clinic.radiologist.request()
                    yield request_rad
                    get_rad_dx_mammo_ts = env.now
                    yield env.process(clinic.rad_review(patient))
                    clinic.scanner.release(request)
                    clinic.radiologist.release(request_rad)
                release_rad_dx_mammo_ts = env.now
                release_dx_scanner_ts = env.now

            # 7. dx us
            if pct_dx_mammo_scheduled < number <= pct_dx_us_scheduled:
                patient_type = 'dx us'
                request = clinic.us_machine.request()
                yield request
                got_us_machine_ts = env.now
                yield env.process(clinic.get_dx_us(patient))

                # rad review
                if rad_change_2:
                    if clinic.radiologist_same_day.count != 0:
                        request_rad = clinic.radiologist.request()
                        yield request_rad
                        get_rad_dx_us_ts = env.now
                        yield env.process(clinic.rad_review(patient))
                        clinic.us_machine.release(request)
                        clinic.radiologist.release(request_rad)
                    else:
                        request_rad_2 = clinic.radiologist_same_day.request()
                        yield request_rad_2
                        # print('7 - Same day rad doing review for dx us at', env.now)
                        get_rad_dx_us_ts = env.now
                        yield env.process(clinic.rad_review(patient))
                        clinic.us_machine.release(request)
                        clinic.radiologist_same_day.release(request_rad_2)
                        # print('7 - Same day rad done doing review for dx us at', env.now)

                else:
                    request_rad = clinic.radiologist.request()
                    yield request_rad
                    get_rad_dx_us_ts = env.now
                    yield env.process(clinic.rad_review(patient))
                    clinic.us_machine.release(request)
                    clinic.radiologist.release(request_rad)
                release_rad_dx_us_ts = env.now
                release_us_machine_ts = env.now

            # 8. us-guided bx
            if pct_dx_us_scheduled < number <= pct_us_guided_bx_scheduled:
                patient_type = 'us bx'
                with clinic.us_machine.request() as request, clinic.radiologist.request() as request_rad:
                    yield request & request_rad
                    got_us_machine_bx_ts = env.now
                    got_scanner_bx_ts = pd.NA
                    yield env.process(clinic.get_us_guided_bx(patient))
                    release_us_machine_after_bx_ts = env.now

                # post bx mammo
                request_2 = clinic.scanner.request()
                yield request_2
                got_scanner_after_us_bx_ts = env.now
                yield env.process(clinic.get_dx_mammo(patient))

                # rad review
                request_rad = clinic.radiologist.request()
                get_rad_ux_bx_ts = env.now
                yield request_rad
                yield env.process(clinic.rad_review(patient))
                clinic.scanner.release(request_2)
                clinic.radiologist.release(request_rad)
                release_rad_us_bx_ts = env.now
                release_scanner_after_post_bx_mammo_ts = env.now

            # 9. mammo-guided bx
            if pct_us_guided_bx_scheduled < number <= pct_mammo_guided_bx_scheduled:
                patient_type = 'mammo bx'
                with clinic.scanner.request() as request, clinic.radiologist.request() as request_rad:
                    yield request & request_rad
                    got_scanner_bx_ts = env.now
                    yield env.process(clinic.get_mammo_guided_bx(patient))
                    # post bx mammo
                    yield env.process(clinic.get_dx_mammo(patient))
                    # rad review
                    get_rad_mammo_bx_ts = env.now
                    yield env.process(clinic.rad_review(patient))
                    clinic.scanner.release(request)
                    clinic.radiologist.release(request_rad)
                    release_rad_mammo_bx_ts = env.now
                    release_scanner_after_post_bx_mammo_ts = env.now

            # 10. screen us
            if pct_mammo_guided_bx_scheduled < number <= pct_screen_us_scheduled:
                patient_type = 'screen us'
                with clinic.us_machine.request() as request:
                    yield request
                    got_screen_us_machine_ts = env.now
                    yield env.process(clinic.get_screen_us(patient))
                    release_screen_us_machine_ts = env.now

            # request a change room
            with clinic.change_room.request() as request:
                yield request
                got_checkout_change_room_ts = env.now
                yield env.process(clinic.use_change_room(patient))
                release_checkout_change_room_ts = env.now

        exit_system_ts = env.now
    else:
        patient_type = ''
        no_show = 'Yes'

    # create dict of timestamps
    timestamps = {'patient_id': patient,
                  'patient_type': patient_type,
                  'arrival_ts': arrival_ts,
                  'got_checkin_staff_ts': got_checkin_staff_ts,
                  'release_checkin_staff_ts': release_checkin_staff_ts,
                  'got_change_room_ts': got_change_room_ts,
                  'release_change_room_ts': release_change_room_ts,
                  'got_public_wait_room_ts': got_public_wait_room_ts,
                  'release_public_wait_room_ts': release_public_wait_room_ts,
                  'got_consent_staff_ts': got_consent_staff_ts,
                  'release_consent_staff_ts': release_consent_staff_ts,
                  'got_gowned_wait_room_ts': got_gowned_wait_room_ts,
                  'release_gowned_wait_room_ts': release_gowned_wait_room_ts,
                  'got_screen_scanner_ts': got_screen_scanner_ts,
                  'release_screen_scanner_ts': release_screen_scanner_ts,
                  'got_dx_scanner_after_ai_ts': got_dx_scanner_after_ai_ts,
                  'release_dx_scanner_after_ai_ts': release_dx_scanner_after_ai_ts,
                  'got_us_machine_after_ai_ts': got_us_machine_after_ai_ts,
                  'release_us_machine_after_ai_ts': release_us_machine_after_ai_ts,
                  'got_dx_scanner_before_us_after_ai_ts': got_dx_scanner_before_us_after_ai_ts,
                  'release_dx_scanner_before_us_after_ai_ts': release_dx_scanner_before_us_after_ai_ts,
                  'got_us_machine_after_dx_scanner_after_ai_ts': got_us_machine_after_dx_scanner_after_ai_ts,
                  'release_dx_scanner_us_machine_after_ai_ts': release_dx_scanner_us_machine_after_ai_ts,
                  'begin_ai_assess_ts': begin_ai_assess_ts,
                  'end_ai_assess_ts': end_ai_assess_ts,
                  'got_dx_scanner_ts': got_dx_scanner_ts,
                  'release_dx_scanner_ts': release_dx_scanner_ts,
                  'got_us_machine_ts': got_us_machine_ts,
                  'release_us_machine_ts': release_us_machine_ts,
                  'got_dx_scanner_before_us_ts': got_dx_scanner_before_us_ts,
                  'release_dx_scanner_before_us_ts': release_dx_scanner_before_us_ts,
                  'got_us_machine_after_dx_scanner_ts': got_us_machine_after_dx_scanner_ts,
                  'release_dx_scanner_us_machine_ts': release_dx_scanner_us_machine_ts,
                  'got_us_machine_bx_ts': got_us_machine_bx_ts,
                  'release_us_machine_after_bx_ts': release_us_machine_after_bx_ts,
                  'got_scanner_bx_ts': got_scanner_bx_ts,
                  'got_scanner_after_us_bx_ts': got_scanner_after_us_bx_ts,
                  'release_scanner_after_post_bx_mammo_ts': release_scanner_after_post_bx_mammo_ts,
                  'got_screen_us_machine_ts': got_screen_us_machine_ts,
                  'release_screen_us_machine_ts': release_screen_us_machine_ts,
                  'got_scanner_after_mri_bx_ts': got_scanner_after_mri_bx_ts,
                  'got_mri_machine_ts': got_mri_machine_ts,
                  'release_mri_machine_ts': release_mri_machine_ts,
                  'got_checkout_change_room_ts': got_checkout_change_room_ts,
                  'release_checkout_change_room_ts': release_checkout_change_room_ts,
                  'get_rad_dx_mammo_ts': get_rad_dx_mammo_ts,
                  'release_rad_dx_mammo_ts': release_rad_dx_mammo_ts,
                  'get_rad_dx_us_ts': get_rad_dx_us_ts,
                  'release_rad_dx_us_ts': release_rad_dx_us_ts,
                  'get_rad_dx_mammo_us_mammo_ts': get_rad_dx_mammo_us_mammo_ts,
                  'release_rad_dx_mammo_us_mammo_ts': release_rad_dx_mammo_us_mammo_ts,
                  'get_rad_dx_mammo_us_us_ts': get_rad_dx_mammo_us_us_ts,
                  'release_rad_dx_mammo_us_us_ts': release_rad_dx_mammo_us_us_ts,
                  'get_rad_ux_bx_ts': get_rad_ux_bx_ts,
                  'release_rad_us_bx_ts': release_rad_us_bx_ts,
                  'get_rad_mri_bx_ts': get_rad_mri_bx_ts,
                  'release_rad_mri_bx_ts': release_rad_mri_bx_ts,
                  'get_rad_mammo_bx_ts': get_rad_mammo_bx_ts,
                  'release_rad_mammo_bx_ts': release_rad_mammo_bx_ts,
                  'get_rad_dx_mammo_us_mammo_after_ai_ts': get_rad_dx_mammo_us_mammo_after_ai_ts,
                  'release_rad_dx_mammo_us_mammo_after_ai_ts': release_rad_dx_mammo_us_mammo_after_ai_ts,
                  'get_rad_dx_mammo_us_us_after_ai_ts': get_rad_dx_mammo_us_us_after_ai_ts,
                  'release_rad_dx_mammo_us_us_after_ai_ts': release_rad_dx_mammo_us_us_after_ai_ts,
                  'get_rad_dx_mammo_after_ai_ts': get_rad_dx_mammo_after_ai_ts,
                  'release_rad_dx_mammo_after_ai_ts': release_rad_dx_mammo_after_ai_ts,
                  'get_rad_dx_us_after_ai_ts': get_rad_dx_us_after_ai_ts,
                  'release_rad_dx_us_after_ai_ts': release_rad_dx_us_after_ai_ts,
                  'exit_system_ts': exit_system_ts,
                  'no_show': no_show,
                  'RSS': RSS,
                  'RSS_recall': RSS_recall,
                  'dx_in_days': dx_in_days,
                  'dx_slot_num': dx_slot_num,
                  'dx_at_day': dx_at_day,
                  'recall_yn': recall_yn,
                  'no_show_prob': number_no_show
                  }
    clinic.timestamps_list.append(timestamps)
