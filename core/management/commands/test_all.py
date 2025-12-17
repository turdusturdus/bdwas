from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Uruchamia dwa zestawy testów: (1) wszystkie bez tagu mongo, (2) tylko tag=mongo."

    def handle(self, *args, **options):
        # Django już dostarcza opcję -v/--verbosity w BaseCommand, więc NIE dodajemy jej sami.
        verbosity = int(options.get("verbosity", 1))

        self.stdout.write(self.style.MIGRATE_HEADING("== UNIT/MOCK (exclude tag=mongo) =="))
        call_command("test", verbosity=verbosity, exclude_tags=["mongo"])

        self.stdout.write(self.style.MIGRATE_HEADING("== INTEGRATION/MONGO (tag=mongo) =="))
        call_command("test", verbosity=verbosity, tags=["mongo"])

        self.stdout.write(self.style.SUCCESS("OK: unit/mock + mongo"))
