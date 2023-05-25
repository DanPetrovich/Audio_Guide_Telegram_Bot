import data


class Location:
    number = 0
    name = ''
    oral_messages_to_forward = []
    written_messages_to_forward = []
    url_to_route = ''


list_of_locations = ['Басманная', 'Покровский бульвар', 'Малый Трехсвятительский и Хитровкский переулки',
                     'Большой Трехсвятительский переулок', 'Мясницкая']

loc_map = {'Мясницкая': 4, 'Покровский бульвар': 1, 'Большой Трехсвятительский переулок': 3,
            'Малый Трехсвятительский и Хитровкский переулки': 2, 'Басманная': 0}

Basmach = Location()
Basmach.url_to_route = 'https://yandex.ru/maps/-/CCUo7-aaSC'
Myasnickaya = Location()
Myasnickaya.url_to_route = 'https://yandex.ru/maps/-/CCUo72Eg~C'
B_Trehsvyat = Location()
B_Trehsvyat.url_to_route = 'https://yandex.ru/maps/-/CCUo72fTWA'
Pokrovka = Location()
Pokrovka.url_to_route = 'https://yandex.ru/maps/-/CCUo72qCCC'
M_Trehsvyat = Location()
M_Trehsvyat.url_to_route = 'https://yandex.ru/maps/-/CCUo72xn9C'

locations = [Basmach, Pokrovka, M_Trehsvyat, B_Trehsvyat,  Myasnickaya]

loc_map_2 = {Myasnickaya: 4, Pokrovka: 1, B_Trehsvyat: 3,
           M_Trehsvyat: 2, Basmach: 0}

loc_dict = {'Басманная': Basmach, 'Мясницкая': Myasnickaya,
            'Большой Трехсвятительский переулок': B_Trehsvyat, 'Покровский бульвар': Pokrovka,
            'Малый Трехсвятительский и Хитровкский переулки': M_Trehsvyat}

Basmach.name = 'Басманной'
Basmach.oral_messages_to_forward = data.Basmach_audio
Basmach.written_messages_to_forward = data.Basmach_text

Myasnickaya.name = 'Мясницкой'
Myasnickaya.written_messages_to_forward = data.Myasnickaya_text
Myasnickaya.oral_messages_to_forward = data.Myasnickaya_audio

B_Trehsvyat.name = 'Большом Трехсвятительском переулке'
B_Trehsvyat.written_messages_to_forward = data.B_Trehsvyat_text
B_Trehsvyat.oral_messages_to_forward = data.B_Trehsvyat_audio

M_Trehsvyat.name = 'Малом Трехсвятительском и Хитровкском переулках'
M_Trehsvyat.written_messages_to_forward = data.M_Trehsvyat_text
M_Trehsvyat.oral_messages_to_forward = data.M_Trehsvyat_audio

Pokrovka.name = 'Покровском бульваре'
Pokrovka.written_messages_to_forward = data.Pokra_text
Pokrovka.oral_messages_to_forward = data.Pokra_audio
