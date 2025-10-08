"""
Common initialization app for the LMS and CMS
"""

from django.apps import AppConfig


class CommonInitializationConfig(AppConfig):  # lint-amnesty, pylint: disable=missing-class-docstring
    name = 'openedx.core.djangoapps.common_initialization'
    verbose_name = 'Common Initialization'

    def ready(self):
        # Common settings validations for the LMS and CMS.
        from . import checks  # lint-amnesty, pylint: disable=unused-import
        self._add_mimetypes()
        self._register_psycopg_adapters()

    @staticmethod
    def _add_mimetypes():
        """
        Add extra mimetypes. Used in xblock_resource.
        """
        import mimetypes

        mimetypes.add_type('application/vnd.ms-fontobject', '.eot')
        mimetypes.add_type('application/x-font-opentype', '.otf')
        mimetypes.add_type('application/x-font-ttf', '.ttf')
        mimetypes.add_type('application/font-woff', '.woff')

    @staticmethod
    def _register_psycopg_adapters():
        """
        Register psycopg3 adapters for opaque_keys types when using PostgreSQL.

        This allows CourseLocator, LibraryLocator, and other opaque key objects
        to be passed directly to Django queries without manual string conversion.
        """
        from django.conf import settings

        # Only register adapters if we're using PostgreSQL
        databases_using_postgres = [
            db_config for db_config in settings.DATABASES.values()
            if 'postgresql' in db_config.get('ENGINE', '').lower() or
               'psycopg' in db_config.get('ENGINE', '').lower()
        ]

        if databases_using_postgres:
            try:
                from psycopg.adapt import Dumper
                from psycopg.adapters import AdaptersMap
                from opaque_keys.edx.keys import OpaqueKey

                class OpaqueKeyDumper(Dumper):
                    """
                    Custom psycopg3 dumper for OpaqueKey subclasses.
                    Converts opaque keys to their string representation for database storage.
                    """
                    def dump(self, obj):
                        return str(obj).encode('utf-8')

                # Register the dumper for OpaqueKey and its subclasses
                # This will handle CourseLocator, LibraryLocator, UsageKey, etc.
                adapters = AdaptersMap.get_global()
                adapters.register_dumper(OpaqueKey, OpaqueKeyDumper)

            except ImportError:
                # psycopg3 is not installed
                pass
