from openpulse.analyzer.releases import (
    classify_release_significance,
    normalize_version,
    version_compare,
)


def test_normalize_version_handles_v_prefix_and_suffixes() -> None:
    assert normalize_version("v1.2.3") == (1, 2, 3)
    assert normalize_version("1.2.3-beta.1") == (1, 2, 3, "beta", 1)


def test_version_compare_detects_major_and_minor_updates() -> None:
    assert version_compare("v1.2.3", "v1.2.4") > 0
    assert version_compare("v1.2.4", "v1.3.0") > 0
    assert version_compare("v2.0.0", "v1.9.9") > 0


def test_classify_release_significance_marks_major_releases() -> None:
    release = {
        "repository": "kubernetes/kubernetes",
        "version": "v1.32.0",
        "release_name": "Kubernetes v1.32.0",
        "is_prerelease": False,
    }
    assert classify_release_significance(release) == "MAJOR"

    prerelease = {
        "repository": "hashicorp/terraform",
        "version": "v1.9.0-rc1",
        "release_name": "Terraform v1.9.0-rc1",
        "is_prerelease": True,
    }
    assert classify_release_significance(prerelease) == "PRE_RELEASE"
