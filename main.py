import sqlite3

from pathlib import Path

from ulauncher.api import Extension, Result
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction


ICON='firefox'


class Firebook(Extension):
    def __init__(self):
        super().__init__()
        self.bookmarks = []

    def on_input(self, input_text, trigger_id):
        query = input_text.lower().strip()

        if not query:
            if not self.preferences['profile']:
                return [Result(icon=ICON,
                               name='The profile path is not set',
                               description='Specify the profile path in the extension settings',
                               on_enter=True)]

            profile = Path(self.preferences['profile']).expanduser()
            if not profile.is_dir():
                return [Result(icon=ICON,
                               name='The provided profile path does not exist',
                               description=f'Double-check the profile path in the extension settings',
                               on_enter=True)]

            places_db = Path(f'{profile}/places.sqlite')
            if not places_db.is_file():
                return [Result(icon=ICON,
                               name='The provided profile path does not have places.sqlite database',
                               description=f'Double-check the profile path in the extension settings',
                               on_enter=True)]

            con = sqlite3.connect(f'file:{places_db}?immutable=1', uri=True)
            cur = con.cursor()
            res = cur.execute('SELECT moz_bookmarks.title, moz_places.url FROM moz_bookmarks JOIN moz_places ON moz_bookmarks.fk = moz_places.id WHERE moz_bookmarks.type = 1;')
            self.bookmarks = cur.fetchall()
            con.close()
            matches = self.bookmarks
        else:
            matches = [i for i in self.bookmarks if query in i[0].lower() or query in i[1].lower()]

        if not matches:
            return [Result(icon=ICON,
                           name='No matches found',
                           description='Try to change the search pattern',
                           on_enter=True)]

        items = []
        for i in matches[:25]:
            items.append(Result(icon=ICON,
                                name=i[0],
                                description=i[1],
                                on_enter=OpenUrlAction(i[1])))
        return items


if __name__ == '__main__':
    Firebook().run()
