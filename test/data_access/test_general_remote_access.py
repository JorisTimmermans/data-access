__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

from multiply_core.observations import DataTypeConstants
from multiply_data_access.general_remote_access import HttpMetaInfoProvider, HttpMetaInfoProviderAccessor
from shapely.wkt import loads

PATH_TO_JSON_FILE = './test/test_data/modis_store.json'
ELES_TEST_URL = 'http://www2.geog.ucl.ac.uk/~ucfafyi/eles/'
EMUS_TEST_URL = 'http://www2.geog.ucl.ac.uk/~ucfafyi/emus/'
CAMS_TEST_URL = 'http://www2.geog.ucl.ac.uk/~ucfafyi/cams/'


def test_meta_info_provider_create():
    parameters = {'path_to_json_file': PATH_TO_JSON_FILE, 'url': EMUS_TEST_URL,
                  'data_types': '{}, TYPE_X'.format(DataTypeConstants.ASTER)}
    provider = HttpMetaInfoProviderAccessor.create_from_parameters(parameters)

    assert provider is not None


def test_meta_info_provider_name():
    parameters = {'path_to_json_file': PATH_TO_JSON_FILE, 'url': EMUS_TEST_URL,
                  'data_types': '{}, TYPE_X'.format(DataTypeConstants.ASTER)}
    provider = HttpMetaInfoProviderAccessor.create_from_parameters(parameters)

    assert 'HttpMetaInfoProvider' == provider.name()
    assert 'HttpMetaInfoProvider' == HttpMetaInfoProvider.name()
    assert 'HttpMetaInfoProvider' == HttpMetaInfoProviderAccessor.name()


def test_meta_info_provider_get_parameters_as_dict():
    parameters = {'path_to_json_file': PATH_TO_JSON_FILE, 'url': EMUS_TEST_URL,
                  'data_types': '{}, TYPE_X'.format(DataTypeConstants.ASTER)}
    provider = HttpMetaInfoProviderAccessor.create_from_parameters(parameters)

    parameters_as_dict = provider._get_parameters_as_dict()

    assert 3 == len(parameters_as_dict)
    assert 'path_to_json_file' in parameters_as_dict.keys()
    assert PATH_TO_JSON_FILE == parameters_as_dict['path_to_json_file']
    assert 'url' in parameters_as_dict.keys()
    assert EMUS_TEST_URL == parameters_as_dict['url']
    assert 'data_types' in parameters_as_dict.keys()
    assert 'ASTER,TYPE_X' == parameters_as_dict['data_types']

# this test is expensive. Execute to test access to elevation data
# def test_query_wrapped_meta_info_provider_eles():
#     parameters = {'path_to_json_file': PATH_TO_JSON_FILE, 'url': ELES_TEST_URL,
#                   'data_types': '{}, TYPE_X'.format(DataTypeConstants.ASTER)}
#     provider = HttpMetaInfoProviderAccessor.create_from_parameters(parameters)
#
#     query_string = 'POLYGON((-6.5 42.7, -6.7 42.6, -6.7 42.1, -6.5 42.1, -6.5 42.7));2017-09-04;2017-09-04;ASTER'
#     data_set_meta_infos = provider._query_wrapped_meta_info_provider(query_string)
#
#     assert 1 == len(data_set_meta_infos)
#     expected_aster_coverage = loads('POLYGON((-7. 42., -7. 43., -6. 43., -6. 42., -7. 42.))')
#     aster_coverage = loads(data_set_meta_infos[0].coverage)
#     assert expected_aster_coverage.almost_equals(aster_coverage)
#     assert '' == data_set_meta_infos[0].start_time
#     assert '' == data_set_meta_infos[0].end_time
#     assert 'ASTER' == data_set_meta_infos[0].data_type
#     assert 'ASTGTM2_N42W007_dem.tif' == data_set_meta_infos[0].identifier


def test_query_wrapped_meta_info_provider_emus():
    parameters = {'path_to_json_file': PATH_TO_JSON_FILE, 'url': EMUS_TEST_URL,
                  'data_types': '{}, {}, {}'.format(DataTypeConstants.S2A_EMULATOR, DataTypeConstants.S2B_EMULATOR,
                                                    DataTypeConstants.WV_EMULATOR)}
    provider = HttpMetaInfoProviderAccessor.create_from_parameters(parameters)

    query_string = 'POLYGON((-6. 42.7, -6.7 42.6, -6.7 42.1, -6. 42.1, -6. 42.7));2017-09-04;2017-09-04;' \
                   'ISO_MSI_A_EMU, ISO_MSI_B_EMU, WV_EMU'
    data_set_meta_infos = provider._query_wrapped_meta_info_provider(query_string)

    assert 13 == len(data_set_meta_infos)
    for i, data_set_meta_info in enumerate(data_set_meta_infos):
        assert 'POLYGON((-180.0 90.0, 180.0 90.0, 180.0 -90.0, -180.0 -90.0, -180.0 90.0))' == \
               data_set_meta_info.coverage
        assert '' == data_set_meta_info.start_time
        assert '' == data_set_meta_info.end_time
        if i < 6:
            assert 'ISO_MSI_A_EMU' == data_set_meta_info.data_type
        elif i < 12:
            assert 'ISO_MSI_B_EMU' == data_set_meta_info.data_type
        else:
            assert 'WV_EMU' == data_set_meta_info.data_type
    assert 'isotropic_MSI_emulators_correction_xap_S2A.pkl' == data_set_meta_infos[0].identifier
    assert 'isotropic_MSI_emulators_correction_xbp_S2A.pkl' == data_set_meta_infos[1].identifier
    assert 'isotropic_MSI_emulators_correction_xcp_S2A.pkl' == data_set_meta_infos[2].identifier
    assert 'isotropic_MSI_emulators_optimization_xap_S2A.pkl' == data_set_meta_infos[3].identifier
    assert 'isotropic_MSI_emulators_optimization_xbp_S2A.pkl' == data_set_meta_infos[4].identifier
    assert 'isotropic_MSI_emulators_optimization_xcp_S2A.pkl' == data_set_meta_infos[5].identifier
    assert 'isotropic_MSI_emulators_correction_xap_S2B.pkl' == data_set_meta_infos[6].identifier
    assert 'isotropic_MSI_emulators_correction_xbp_S2B.pkl' == data_set_meta_infos[7].identifier
    assert 'isotropic_MSI_emulators_correction_xcp_S2B.pkl' == data_set_meta_infos[8].identifier
    assert 'isotropic_MSI_emulators_optimization_xap_S2B.pkl' == data_set_meta_infos[9].identifier
    assert 'isotropic_MSI_emulators_optimization_xbp_S2B.pkl' == data_set_meta_infos[10].identifier
    assert 'isotropic_MSI_emulators_optimization_xcp_S2B.pkl' == data_set_meta_infos[11].identifier
    assert 'wv_MSI_retrieval_S2A.pkl' == data_set_meta_infos[12].identifier