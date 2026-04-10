"""Integration tests for SiteRepository CRUD operations."""

import tempfile
from decimal import Decimal
from pathlib import Path

import pytest

from api_finance_dashboard.data.database import init_database
from api_finance_dashboard.data.models import Currency, SiteType
from api_finance_dashboard.data.site_repository import SiteRepository


@pytest.fixture
def repo(tmp_path):
    db_path = tmp_path / "test.db"
    init_database(db_path)
    return SiteRepository(db_path)


class TestSiteRepository:
    def test_create_and_read(self, repo):
        site = repo.create(
            name="Test Site",
            site_type=SiteType.UPSTREAM,
            url="https://example.com",
            panel_type="new-api",
            currency=Currency.USD,
            alert_threshold=Decimal("5.00"),
        )
        assert site.name == "Test Site"
        assert site.type == SiteType.UPSTREAM
        assert site.currency == Currency.USD
        assert site.alert_threshold == Decimal("5.00")

    def test_get_all_ordered(self, repo):
        repo.create(name="Upstream B", site_type=SiteType.UPSTREAM, url="https://b.com")
        repo.create(name="Main Site", site_type=SiteType.MAIN, url="https://main.com")
        repo.create(name="Upstream A", site_type=SiteType.UPSTREAM, url="https://a.com")

        sites = repo.get_all()
        assert len(sites) == 3
        assert sites[0].type == SiteType.MAIN  # main first
        assert sites[1].name == "Upstream A"   # then alphabetical
        assert sites[2].name == "Upstream B"

    def test_update(self, repo):
        site = repo.create(name="Old Name", site_type=SiteType.UPSTREAM, url="https://old.com")
        updated = repo.update(site.id, name="New Name", url="https://new.com")
        assert updated.name == "New Name"
        assert updated.url == "https://new.com"

    def test_delete(self, repo):
        site = repo.create(name="To Delete", site_type=SiteType.UPSTREAM, url="https://del.com")
        assert repo.delete(site.id) is True
        assert repo.get_by_id(site.id) is None

    def test_create_with_dashboard_url(self, repo):
        site = repo.create(
            name="Upstream With Dashboard",
            site_type=SiteType.UPSTREAM,
            url="https://upstream.com/log",
            dashboard_url="https://upstream.com/dashboard",
            panel_type="new-api",
            currency=Currency.USD,
        )
        assert site.dashboard_url == "https://upstream.com/dashboard"

    def test_create_without_dashboard_url(self, repo):
        site = repo.create(
            name="Main Site",
            site_type=SiteType.MAIN,
            url="https://main.com/log",
        )
        assert site.dashboard_url is None

    def test_update_dashboard_url(self, repo):
        site = repo.create(
            name="Upstream",
            site_type=SiteType.UPSTREAM,
            url="https://upstream.com/log",
        )
        updated = repo.update(site.id, dashboard_url="https://upstream.com/dash")
        assert updated.dashboard_url == "https://upstream.com/dash"

    def test_delete_nonexistent(self, repo):
        assert repo.delete(999) is False

    def test_get_by_id_nonexistent(self, repo):
        assert repo.get_by_id(999) is None
