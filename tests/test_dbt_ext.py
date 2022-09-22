from dbt_ext.main import app


def test_app_name():
    assert app.info.name == "dbt"
