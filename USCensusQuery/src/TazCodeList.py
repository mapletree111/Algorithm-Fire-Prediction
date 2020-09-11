"""
When aggregating, TAZs into larger geometries, sum these values.
When separating TAZs into smaller geometries or clipping, multiply by the proportion
of the smaller geometry
"""
taz_to_sum = \
    [
        'TPE_HH',  # num households
        'TPE_POP',  # Total population
        'TPE_POP_HH',  # Total household pop
        'TPE_POP_GR',  # Group quarters pop
        'TPE_LOINC',  # number of manuf, industrial, etc. employees
        'TPE_HIINC',  # number of construction, communication, etc. employees
        'TPE_RTL',  # retail employees
        'TPE_HWY',  # highway retail employess
        'TPE_LOSVC',  # low-visitor service employees
        'TPE_HISVC',  # high visitor service employees
        'TPE_OFFGOV',  # office and gov employees
        'TPE_EDUC',  # school, college, university employees
        'TPE_STU_K8',
        'TPE_STU_HS',
        'TPE_STU_CU',
        'TPE_TOTEMP',
        'TPE_AREA_L', # Area in sq mi, minus bodies of water


        # Street Metrics
        # u'ST_NumStSeg',
        # u'ST_TotStLen',
        # u'ST_IntCnt',
    ]

"""
Labels - Do not modify these when combining geometries
"""
taz_no_mod = \
    [
        'TPE_DORM',
        'SUBCODIST',
        'CORR',
        'STATION',
        'SPHOFINFL',
        'MPORPO2010',
        'MPORPO2000',
        'PUMA',
        'PUMA_2000',
        'ORDER',
        'orig_ogc_f',
    ]

"""
When aggregating, TAZs into larger geometries, average these values.
When separating TAZs into smaller geometries, give these values to all subdivisions
"""
taz_to_avg = \
    [

        u'ST_Mesh',
        u'ST_AvgSpeed',
        u'ST_SdvSpeed',
        u'ST_PctLocal',
        u'ST_PctFwy',
        u'ST_PctOther',
        u'ST_RdDens',
        u'ST_IntDens'
    ]

def get_taz_quantitative():
    return taz_to_sum + taz_to_avg