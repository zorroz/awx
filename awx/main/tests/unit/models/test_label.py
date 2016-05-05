import pytest

from awx.main.models.label import Label
from awx.main.models.unified_jobs import UnifiedJobTemplate, UnifiedJob


def test_get_orphaned_labels(mocker):
    mock_query_set = mocker.MagicMock()
    Label.objects.filter = mocker.MagicMock(return_value=mock_query_set)

    ret = Label.get_orphaned_labels()

    assert mock_query_set == ret
    Label.objects.filter.assert_called_with(organization=None, jobtemplate_labels__isnull=True)

def test_is_detached(mocker):
    mock_query_set = mocker.MagicMock()
    Label.objects.filter = mocker.MagicMock(return_value=mock_query_set)
    mock_query_set.count.return_value = 1

    label = Label(id=37)
    ret = label.is_detached()

    assert ret is True
    Label.objects.filter.assert_called_with(id=37, unifiedjob_labels__isnull=True, unifiedjobtemplate_labels__isnull=True)
    mock_query_set.count.assert_called_with()

def test_is_detached_not(mocker):
    mock_query_set = mocker.MagicMock()
    Label.objects.filter = mocker.MagicMock(return_value=mock_query_set)
    mock_query_set.count.return_value = 0

    label = Label(id=37)
    ret = label.is_detached()

    assert ret is False
    Label.objects.filter.assert_called_with(id=37, unifiedjob_labels__isnull=True, unifiedjobtemplate_labels__isnull=True)
    mock_query_set.count.assert_called_with()

@pytest.mark.parametrize("jt_count,j_count,expected", [
    (1, 0, True),
    (0, 1, True),
    (1, 1, False),
])
def test_is_candidate_for_detach(mocker, jt_count, j_count, expected):
    mock_job_qs = mocker.MagicMock()
    mock_job_qs.count = mocker.MagicMock(return_value=j_count)
    UnifiedJob.objects = mocker.MagicMock()
    UnifiedJob.objects.filter = mocker.MagicMock(return_value=mock_job_qs)

    mock_jt_qs = mocker.MagicMock()
    mock_jt_qs.count = mocker.MagicMock(return_value=jt_count)
    UnifiedJobTemplate.objects = mocker.MagicMock()
    UnifiedJobTemplate.objects.filter = mocker.MagicMock(return_value=mock_jt_qs)

    label = Label(id=37)
    ret = label.is_candidate_for_detach()

    UnifiedJob.objects.filter.assert_called_with(labels__in=[label.id])
    UnifiedJobTemplate.objects.filter.assert_called_with(labels__in=[label.id])
    mock_job_qs.count.assert_called_with()
    mock_jt_qs.count.assert_called_with()

    assert ret is expected
