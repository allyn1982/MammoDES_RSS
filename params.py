import pandas as pd

def screener_type_1ss(number):
    if number <= 0.7:
        patient_type = 'screen + dx mammo us'
    elif 0.85 >= number > 0.7:
        patient_type = 'screen + dx mammo'
    else:
        patient_type = 'screen + dx us'
    return patient_type

def exam_percent_dict(dict, exam_type_list, value_list):
    for exam_type, value in zip(exam_type_list, value_list):
        dict[exam_type] = value
    return dict

def exam_type_prob(time):
    if time <= 1.0: #7-8
        return dict_7_8
    elif time <= 2.0 and time > 1.0: #8-9
        return dict_8_9
    elif time <=3.0 and time > 2.0: #9-10
        return dict_9_10
    elif time <=4.0 and time > 3.0: # 10-11
        return dict_10_11
    elif time <=5.0 and time > 4.0: # 11-12
        return dict_11_12
    elif time <=6.0 and time > 5.0: # 12-13
        return dict_12_13
    elif time <=7.0 and time > 6.0: # 13-14
        return dict_13_14
    elif time <=8.0 and time > 7.0: # 14-15
        return dict_14_15
    elif time <=9.0 and time > 8.0: # 15-16
        return dict_15_16
    elif time <=10.0 and time > 9.0: #16-17
        return dict_16_17

#  dicts specifying % of exam at each hour
exam_percent_df = pd.read_csv('./data/exam_percent.csv')
# rearrange columns
# seq: screen mammo, dx mammo us, dx mammo, dx us, bx us, bx mammo, screen us, bx mri, mri
new_list = ['Screen Mammo', 'Dx Mammo + Dx US', 'Dx Mammo', 'Dx US', 'Bx US', 'Bx Mammo', 'Screen US', 'Bx MRI', 'MRI']
exam_percent_df['new_order'] = exam_percent_df['exam_type_new'].apply(lambda x: new_list.index(x))
exam_percent_df = exam_percent_df.sort_values(by='new_order').reset_index(drop=True)
exam_percent_df = exam_percent_df.drop(columns='new_order')

exam_type_list = ['screen', 'dx mammo us', 'dx mammo',  'dx us',
                   'us bx', 'mammo bx', 'screen us', 'mri-guided bx', 'mri']
dict_7_8 = {}
dict_7_8 = exam_percent_dict(dict_7_8, exam_type_list, list(exam_percent_df.h_7))

dict_8_9 = {}
dict_8_9 = exam_percent_dict(dict_8_9, exam_type_list, list(exam_percent_df.h_8))

dict_9_10 = {}
dict_9_10 = exam_percent_dict(dict_9_10, exam_type_list, list(exam_percent_df.h_9))

dict_10_11 = {}
dict_10_11 = exam_percent_dict(dict_10_11, exam_type_list, list(exam_percent_df.h_10))

dict_11_12 = {}
dict_11_12 = exam_percent_dict(dict_11_12, exam_type_list, list(exam_percent_df.h_11))

dict_12_13 = {}
dict_12_13 = exam_percent_dict(dict_12_13, exam_type_list, list(exam_percent_df.h_12))

dict_13_14 = {}
dict_13_14 = exam_percent_dict(dict_13_14, exam_type_list, list(exam_percent_df.h_13))

dict_14_15 = {}
dict_14_15 = exam_percent_dict(dict_14_15, exam_type_list, list(exam_percent_df.h_14))

dict_15_16 = {}
dict_15_16 = exam_percent_dict(dict_15_16, exam_type_list, list(exam_percent_df.h_15))

dict_16_17 = {}
dict_16_17 = exam_percent_dict(dict_16_17, exam_type_list, list(exam_percent_df.h_16))

