"""测试设施自检：被测模块可导入、fixture 可用。"""


def test_service_fixture_constructs(service):
    assert service.store is not None
    assert service.aria2 is not None
