import data


class Location:
    number = 0
    name = ''
    oral_messages_to_forward = []
    written_messages_to_forward = []
    photos = []


list_of_locations = ['Басмач', 'Покровка', 'Малый трехсвят и Хитровка',
                     'Большой трехсвят', 'Армянский переулок', 'Мясницкая']

loc_map = {'Армянский переулок': 4, 'Мясницкая': 5, 'Покровка': 1, 'Большой трехсвят': 3,
           'Малый трехсвят и Хитровка': 2, 'Басмач': 0}

Basmach = Location()

Myasnickaya = Location()
Krivokolennyi = Location()
Armyanskii = Location()
B_Trehsvyat = Location()
Pokrovka = Location()
M_Trehsvyat = Location()

locations = [Basmach, Armyanskii, B_Trehsvyat, Pokrovka, M_Trehsvyat]

loc_dict = {'Басмач': Basmach, 'Мясницкая': Myasnickaya, 'Армянский переулок': Armyanskii,
            'Большой трехсвят': B_Trehsvyat, 'Покровка': Pokrovka, 'Малый трехсвят и Хитровка': M_Trehsvyat}

for key, val in loc_dict.items():
    val.name = key
    val.number = loc_map[key]

Basmach.oral_messages_to_forward = data.Basmach_audio
