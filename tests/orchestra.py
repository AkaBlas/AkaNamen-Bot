#!/usr/bin/env python
"""Provide an orchestra to tests"""
import random
import datetime as dt
from components import Gender, instruments, Member, Orchestra


def value_or_none(value):
    return random.choice([None, value])


def first_name(gender):
    male_names = [
        'Santiago',
        'Mateo',
        'Matías',
        'Diego',
        'Sebastián',
        'Nicolás',
        'Miguel',
        'Ángel',
        'Iker',
        'Alejandro',
        'Samuel',
        'Liam',
        'Noah',
        'William',
        'James',
        'Logan',
        'Benjamin',
        'Mason',
        'Elijah',
        'Oliver',
        'Jacob',
    ]
    female_names = [
        'Emma',
        'Olivia',
        'Ava',
        'Isabella',
        'Sophia',
        'Taylor',
        'Charlotte',
        'Amelia',
        'Evelyn',
        'Abigail',
        'Mary',
        'Patricia',
        'Linda',
        'Barbara',
        'Elizabeth',
        'Jennifer',
        'Maria',
        'Susan',
        'Margaret',
        'Dorothy',
    ]

    if gender == Gender.MALE:
        name = random.choice(male_names)
    else:
        name = random.choice(female_names)
    return value_or_none(name)


def last_name():
    name = random.choice(
        [
            'Gruber',
            'Huber',
            'Bauer',
            'Wagner',
            'Müller',
            'Pichler',
            'Steiner',
            'Moser',
            'Mayer',
            'Hofer',
            'Leitner',
            'Berger',
            'Fuchs',
            'Eder',
            'Fischer',
            'Schmid',
            'Winkler',
            'Weber',
            'Schwarz',
            'Maier',
            'Schneider',
            'Reiter',
            'Mayr',
            'Schmidt',
            'Wimmer',
            'Egger',
            'Brunner',
            'Lang',
            'Baumgartner',
            'Auer',
            'Binder',
            'Lechner',
            'Wolf',
            'Wallner',
            'Aigner',
            'Ebner',
            'Koller',
            'Lehner',
            'Haas',
            'Schuster',
        ]
    )
    return value_or_none(name)


def nickname():
    name = random.choice(
        [
            'Bama',
            'Rock',
            'Boner',
            'No. 3',
            'Big Boy',
            'Conan the Republican',
            'Jazzman',
            'Pablo',
            'Pedro',
            'Hogan',
            'Big George',
            'Freddy Boy',
            'Freddo',
            'Congressman Kickass',
            'Nellie',
            'Benny',
            'Benator',
            'Ellis',
            'Ali',
            'Frazier',
            'Sabertooth',
            'Red',
            'Big Time',
            'Vice',
            'Rummy',
            'Izzy',
            'Altoid Boy',
            'Boy Genius',
            'Turd Blossom',
            'The Architect',
            'Condi',
            'Guru',
            'The World\'s Greatest Hero',
            'Big O',
            'Pablo',
            'Fredo',
            'Barty',
            'Bart',
            'Danny Boy',
            'Captain Dan',
            'Dan the Man',
            'Ari-Bob',
            'High Prophet',
            'Hurricane Karen',
            'The Blade',
            'My Man Mitch',
            'Big Country',
            'Brownie',
            'Brother George',
            'Tree Man',
            'La Margarita',
            'Tangent Man',
            'Tiny',
            'Light Bulb',
            'Bullets',
            'M&M',
            'Horny',
            'Scrote',
        ]
    )
    return value_or_none(name)


def phone_number():
    return value_or_none(f'+49{random.randint(10 ** (12 - 1), (10 ** 12) - 1)}')


def date_of_birth():
    earliest = dt.date(1980, 1, 1)
    latest = dt.date(2002, 12, 31)
    return value_or_none(earliest + random.random() * (latest - earliest))


def instrument():
    number = random.randint(1, 3)
    instruments_ = random.sample(
        [i() for i in instruments.__dict__.values() if isinstance(i, type)], number
    )
    return value_or_none(instruments_)


def address():
    address_ = random.choice(
        [
            '777 Brockton Avenue, Abington MA 2351',
            '30 Memorial Drive, Avon MA 2322',
            '250 Hartford Avenue, Bellingham MA 2019',
            '700 Oak Street, Brockton MA 2301',
            '591 Memorial Dr, Chicopee MA 1020',
            '42 Fairhaven Commons Way, Fairhaven MA 2719',
            '337 Russell St, Hadley MA 1035',
            '295 Plymouth Street, Halifax MA 2338',
            '1775 Washington St, Hanover MA 2339',
            '280 Washington Street, Hudson MA 1749',
            '20 Soojian Dr, Leicester MA 1524',
            '11 Jungle Road, Leominster MA 1453',
            '301 Massachusetts Ave, Lunenburg MA 1462',
            '780 Lynnway, Lynn MA 1905',
            '70 Pleasant Valley Street, Methuen MA 1844',
            '1470 S Washington St, North Attleboro MA 2760',
            '72 Main St, North Reading MA 1864',
            '200 Otis Street, Northborough MA 1532',
            '180 North King Street, Northhampton MA 1060',
            '555 East Main St, Orange MA 1364',
            '300 Colony Place, Plymouth MA 2360',
            '36 Paramount Drive, Raynham MA 2767',
            '450 Highland Ave, Salem MA 1970',
            '1180 Fall River Avenue, Seekonk MA 2771',
            '1105 Boston Road, Springfield MA 1119',
            '100 Charlton Road, Sturbridge MA 1566',
            '262 Swansea Mall Dr, Swansea MA 2777',
            '333 Main Street, Tewksbury MA 1876',
            '352 Palmer Road, Ware MA 1082',
            '297 Grant Avenue, Auburn NY 13021',
            '4133 Veterans Memorial Drive, Batavia NY 14020',
            '5399 W Genesse St, Camillus NY 13031',
            '30 Catskill, Catskill NY 12414',
            '3018 East Ave, Central Square NY 13036',
            '139 Merchant Place, Cobleskill NY 12043',
            '2465 Hempstead Turnpike, East Meadow NY 11554',
            '6438 Basile Rowe, East Syracuse NY 13057',
            '10401 Bennett Road, Fredonia NY 14063',
            '100 Elm Ridge Center Dr, Greece NY 14626',
            '103 North Caroline St, Herkimer NY 13350',
            '2 Gannett Dr, Johnson City NY 13790',
            '350 E Fairmount Ave, Lakewood NY 14750',
            '579 Troy-Schenectady Road, Latham NY 12110',
            '43 Stephenville St, Massena NY 13662',
            '750 Middle Country Road, Middle Island NY 11953',
            '4765 Commercial Drive, New Hartford NY 13413',
            '2473 Hackworth Road, Adamsville AL 35005',
            '630 Coonial Promenade Pkwy, Alabaster AL 35007',
            '540 West Bypass, Andalusia AL 36420',
            '5560 Mcclellan Blvd, Anniston AL 36206',
            '1011 US Hwy 72 East, Athens AL 35611',
            '1717 South College Street, Auburn AL 36830',
            '701 Mcmeans Ave, Bay Minette AL 36507',
            '750 Academy Drive, Bessemer AL 35022',
            '1600 Montclair Rd, Birmingham AL 35210',
            '5919 Trussville Crossings Pkwy, Birmingham AL 35235',
            '9248 Parkway East, Birmingham AL 35206',
            '2041 Douglas Avenue, Brewton AL 36426',
            '1916 Center Point Rd, Center Point AL 35215',
            '1950 W Main St, Centre AL 35960',
            '1415 7Th Street South, Clanton AL 35045',
            '626 Olive Street Sw, Cullman AL 35055',
            '3300 South Oates Street, Dothan AL 36301',
            '4310 Montgomery Hwy, Dothan AL 36303',
            '600 Boll Weevil Circle, Enterprise AL 36330',
            '3176 South Eufaula Avenue, Eufaula AL 36027',
            '7100 Aaron Aronov Drive, Fairfield AL 35064',
            '10040 County Road 48, Fairhope AL 36533',
            '3100 Hough Rd, Florence AL 35630',
            '2200 South Mckenzie St, Foley AL 36535',
            '340 East Meighan Blvd, Gadsden AL 35903',
            '890 Odum Road, Gardendale AL 35071',
            '1608 W Magnolia Ave, Geneva AL 36340',
            '501 Willow Lane, Greenville AL 36037',
            '170 Fort Morgan Road, Gulf Shores AL 36542',
            '1706 Military Street South, Hamilton AL 35570',
            '209 Lakeshore Parkway, Homewood AL 35209',
            '2780 John Hawkins Pkwy, Hoover AL 35244',
            '11610 Memorial Pkwy South, Huntsville AL 35803',
            '2200 Sparkman Drive, Huntsville AL 35810',
            '6140A Univ Drive, Huntsville AL 35806',
            '4206 N College Ave, Jackson AL 36545',
            '1625 Pelham South, Jacksonville AL 36265',
            '8551 Whitfield Ave, Leeds AL 35094',
            '8650 Madison Blvd, Madison AL 35758',
            '6350 Cottage Hill Road, Mobile AL 36609',
            '2500 Dawes Road, Mobile AL 36695',
            '685 Schillinger Rd, Mobile AL 36695',
            '3371 S Alabama Ave, Monroeville AL 36460',
            '10710 Chantilly Pkwy, Montgomery AL 36117',
            '3801 Eastern Blvd, Montgomery AL 36116',
            '6495 Atlanta Hwy, Montgomery AL 36117',
            '851 Ann St, Montgomery AL 36107',
            '517 West Avalon Ave, Muscle Shoals AL 35661',
            '5710 Mcfarland Blvd, Northport AL 35476',
            '2900 Pepperrell Pkwy, Opelika AL 36801',
            '92 Plaza Lane, Oxford AL 36203',
            '2181 Pelham Pkwy, Pelham AL 35124',
            '165 Vaughan Ln, Pell City AL 35125',
            '1903 Cobbs Ford Rd, Prattville AL 36066',
            '1095 Industrial Pkwy, Saraland AL 36571',
            '214 Haynes Street, Talladega AL 35160',
            '1300 Gilmer Ave, Tallassee AL 36078',
            '34301 Hwy 43, Thomasville AL 36784',
            '1501 Skyland Blvd E, Tuscaloosa AL 35405',
            '3501 20th Av, Valley AL 36854',
            '1300 Montgomery Highway, Vestavia Hills AL 35216',
            'Universitätsplatz 2, 38106 Braunschweig',
            'Hammervej 20, 7160 Tørring, Dänemark',
            'Münzstraße 5, 38100 Braunschweig',
            'Bültenweg 74-75, 38106 Braunschweig',
        ]
    )
    return value_or_none(address_)


class PhotoFileID:
    @classmethod
    def photo_file_id(cls, bot, chat_id):
        return str(random.randint(5, 555))


def orchestra(members, bot, chat_id, skip=None):
    if skip is None:
        skip = []
    orchestra_ = Orchestra()

    for i in range(1, members):
        gender = random.choice([Gender.MALE, Gender.FEMALE])
        phone_number_ = phone_number() if 'phone_number' not in skip else None
        first_name_ = first_name(gender) if 'first_name' not in skip else None
        last_name_ = last_name() if 'last_name' not in skip else None
        nickname_ = nickname() if 'nickname' not in skip else None
        date_of_birth_ = date_of_birth() if 'date_of_birth' not in skip else None
        instruments_ = instrument() if 'instruments' not in skip else None
        address_ = address() if 'address' not in skip else None
        photo_file_id_ = (
            PhotoFileID.photo_file_id(bot, chat_id) if 'photo_file_id' not in skip else None
        )
        orchestra_.register_member(
            Member(
                user_id=i,
                phone_number=phone_number_,
                first_name=first_name_,
                last_name=last_name_,
                nickname=nickname_,
                gender=gender,
                date_of_birth=date_of_birth_,
                instruments=instruments_,
                address=address_,
                photo_file_id=photo_file_id_,
            )
        )
    return orchestra_
