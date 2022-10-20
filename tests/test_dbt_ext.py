from unittest.mock import patch


def test_app_name(monkeypatch):
    monkeypatch.setenv("DBT_EXT_TYPE", "test")
    from dbt_ext.main import app

    assert app.info.name == "dbt"


def test_pre_invoke(monkeypatch):
    """Verify that pre-invokes are skipped for deps and clean."""
    monkeypatch.setenv("DBT_EXT_TYPE", "test")
    from dbt_ext.main import dbt

    dbt_ext = dbt()

    dbt_ext.skip_pre_invoke = True
    with patch.object(dbt_ext.dbt_invoker, "run_and_log") as mock_run_and_log:
        dbt_ext.pre_invoke("deps", [])
        mock_run_and_log.assert_not_called()

        dbt_ext.pre_invoke("clean", [])
        mock_run_and_log.assert_not_called()

        dbt_ext.pre_invoke("run", [])
        mock_run_and_log.assert_not_called()

    dbt_ext.skip_pre_invoke = False
    with patch.object(dbt_ext.dbt_invoker, "run_and_log") as mock_run_and_log:
        dbt_ext.pre_invoke("deps", [])
        mock_run_and_log.assert_not_called()

        dbt_ext.pre_invoke("clean", [])
        mock_run_and_log.assert_not_called()

        dbt_ext.pre_invoke("run", [])
        assert mock_run_and_log.call_count == 2
        assert mock_run_and_log.call_args_list[0][0][0] == "clean"
        assert mock_run_and_log.call_args_list[1][0][0] == "deps"
