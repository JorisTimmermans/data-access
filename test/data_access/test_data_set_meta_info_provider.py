from multiply_data_access.data_set_meta_info_provider import DataSetMetaInfoProvider, AWS_S2_Meta_Info_Provider

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"

path_to_s2_dir = './test/test_data/aws_s2_data/29/S/QB/2017/9/4/0/'


def test_aws_s2_meta_info_provider():
    provider = AWS_S2_Meta_Info_Provider()
    assert 'AWS_S2_L1C' == provider.name()
    data_set_meta_info = provider.extract_meta_info(path_to_s2_dir)
    assert 'AWS_S2_L1C' == data_set_meta_info.data_type
    assert path_to_s2_dir == data_set_meta_info.identifier
    assert '2017-09-04 11:18:25.839' == data_set_meta_info.start_time
    assert '2017-09-04 11:18:25.839' == data_set_meta_info.end_time
    assert 'POLYGON((-6.724926539250627 37.92559054724302, -5.4774490849610435 37.89483865860684, ' \
           '-5.5234456557459835 36.906971812661624, -6.754676710360797 36.936650397219594, ' \
           '-6.724926539250627 37.92559054724302))' == data_set_meta_info.coverage