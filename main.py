import sqlite3

from pathlib import Path

from ulauncher.api import Extension, Result
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.utils.fuzzy_search import get_score


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
                               name='The profile path is not configured',
                               description='Set the profile path in the extension settings',
                               on_enter=True)]

            profile = Path(self.preferences['profile']).expanduser()
            if not profile.is_dir():
                return [Result(icon=ICON,
                               name='The configured profile path does not exist',
                               description='Double-check the profile path in the extension settings',
                               on_enter=True)]

            places_db = Path(f'{profile}/places.sqlite')
            if not places_db.is_file():
                return [Result(icon=ICON,
                               name='The configured profile path does not have places.sqlite database',
                               description='Double-check the profile path in the extension settings',
                               on_enter=True)]

            con = sqlite3.connect(f'file:{places_db}?immutable=1', uri=True)
            cur = con.cursor()
            res = cur.execute('SELECT moz_bookmarks.title, moz_places.url FROM moz_bookmarks JOIN moz_places ON moz_bookmarks.fk = moz_places.id WHERE moz_bookmarks.type = 1;')
            self.bookmarks = cur.fetchall()
            con.close()
            matches = self.bookmarks
        else:
            if trigger_id == 'fuzzy':
                fuzzy_scores = sorted(self.bookmarks, key=lambda fn: get_score(query, f'{fn[0]} {fn[1]}'), reverse=True)
                matches = list(filter(lambda fn: get_score(query, f'{fn[0]} {fn[1]}') > self.preferences['threshold'], fuzzy_scores))
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
                                name=f'{i[0]} -- {i[1]}' if self.preferences['compact'] else i[0],
                                description=i[1],
                                compact=self.preferences['compact'],
                                highlightable=self.preferences['highlight'],
                                on_enter=OpenUrlAction(i[1])))
        return items


if __name__ == '__main__':
    Firebook().run()
