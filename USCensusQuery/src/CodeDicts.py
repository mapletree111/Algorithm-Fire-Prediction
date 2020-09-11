all_label_dicts = {
    # 'female_label_dict':
    #     {
    # 'f00_5': 'B01001_027E',
    # 'f05_9': 'B01001_028E',
    # 'f10_14': 'B01001_029E',
    # 'f15_17': 'B01001_030E',
    # 'f18_19': 'B01001_031E',
    # 'f20': 'B01001_032E',
    # 'f21': 'B01001_033E',
    # 'f22_24': 'B01001_034E',
    # 'f25_29': 'B01001_035E',
    # 'f30_34': 'B01001_036E',
    # 'f35_39': 'B01001_037E',
    # 'f40_44': 'B01001_038E',
    # 'f45_49': 'B01001_039E',
    # 'f50_54': 'B01001_040E',
    # 'f55_59': 'B01001_041E',
    # 'f60_61': 'B01001_042E',
    # 'f62_64': 'B01001_043E',
    # 'f65_66': 'B01001_044E',
    # 'f67_69': 'B01001_045E',
    # 'f70_74': 'B01001_046E',
    # 'f75_79': 'B01001_047E',
    # 'f80_84': 'B01001_048E',
    # 'f85+': 'B01001_049E',
    #     'fpop': 'B01001_026E'
    # },

    # 'male_label_dict':
    #     {
    # 'm00_5': 'B01001_003E',
    # 'm05_9': 'B01001_004E',
    # 'm10_14': 'B01001_005E',
    # 'm15_17': 'B01001_006E',
    # 'm18_19': 'B01001_007E',
    # 'm20': 'B01001_008E',
    # 'm21': 'B01001_009E',
    # 'm22_24': 'B01001_010E',
    # 'm25_29': 'B01001_011E',
    # 'm30_34': 'B01001_012E',
    # 'm35_39': 'B01001_013E',
    # 'm40_44': 'B01001_014E',
    # 'm45_49': 'B01001_015E',
    # 'm50_54': 'B01001_016E',
    # 'm55_59': 'B01001_017E',
    # 'm60_61': 'B01001_018E',
    # 'm62_64': 'B01001_019E',
    # 'm65_66': 'B01001_020E',
    # 'm67_69': 'B01001_021E',
    # 'm70_74': 'B01001_022E',
    # 'm75_79': 'B01001_023E',
    # 'm80_84': 'B01001_024E',
    # 'm85+': 'B01001_025E',
    #     'mpop': 'B01001_002E'
    # },

    'non_pop_label_dict':
    # Any measures of center go here
        {'bldavg': 'B25035_001E',
         'medinc': 'B06011_001E'
         },
    #
    'other_label_dict':
        {
            'employ': 'B23001_001E',
            'totpop': 'B01001_001E',
            # 'LoEd': 'B15003_002E',
            'pov': 'B17005_002E'
        },
    #
    # 'race_label_dict':
    #     {'pop_a': 'B01001D_001E',
    #      'pop_b': 'B01001B_001E',
    #      'pop_h': 'B01001I_001E',
    #      'pop_i': 'B01001E_001E',
    #      'pop_n': 'B01001C_001E',
    #      'pop_o': 'B01001F_001E',
    #      'pop_w': 'B01001A_001E'}
}


def get_flattened_label_dict():
    return {v: v2 for _, v in all_label_dicts.iteritems() for v, v2 in v.iteritems()}


def get_flattened_code_dict():
    return {v: v2 for _, v in get_all_code_dicts().iteritems() for v, v2 in v.iteritems()}


def get_all_code_dicts():
    return {k: flip(v) for k, v in all_label_dicts.iteritems()}


def flip(dct):
    return {dct[x]: x for x in dct}


def get_all_labels():
    return [label for nst in all_label_dicts.itervalues() for label in nst.iterkeys()]


def iterlabels():
    return (label for nst in all_label_dicts.itervalues() for label in nst.iterkeys())


def get_pop_labels():
    return filter(lambda lbl: lbl not in all_label_dicts['non_pop_label_dict'].keys(), iterlabels())


def get_np_labels():
    return filter(lambda lbl: lbl in all_label_dicts['non_pop_label_dict'].keys(), iterlabels())
