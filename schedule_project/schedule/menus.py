# -*- coding: utf8 -*-
from menu import Menu, MenuItem
from django.core.urlresolvers import reverse

Menu.add_item('teacher', MenuItem('Свободное время',
    reverse('schedule.views.free_time'),
    weight=10,))

Menu.add_item('teacher', MenuItem('Добавить ученика',
    reverse('schedule.views.add_student'),
    weight=20,))

Menu.add_item('admin', MenuItem('Добавить ученика',
    reverse('schedule.views.add_student'),
    weight=50,))

# Menu.add_item('main', MenuItem('К просмотру',
#     reverse('movies.views.list', kwargs=({'list': 'to-watch'})),
#     weight=10,))


# feed_children = (
#     MenuItem('Друзья',
#         reverse('movies.views.feed', kwargs=({'list': 'friends'})),
#         weight=20,),
#     MenuItem('Люди',
#         reverse('movies.views.feed', kwargs=({'list': 'people'})),
#         weight=20,),
# )

# Menu.add_item('main', MenuItem('Лента',
#     reverse('movies.views.search'),  # doesn't really matter because of the submenus
#     weight=20,
#     children=feed_children))
