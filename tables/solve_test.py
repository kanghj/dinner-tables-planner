import uuid
from unittest import TestCase
from .solve import partition, community_and_persons_from_file
import pytest


class SolverTest(TestCase):

    def setUp(self):
        self.large_community = {
            0: [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110],
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            2: [1, 11, 21, 31, 41, 51, 61, 71, 81, 91, 101, 111, 121, 131, 141, 151, 161],
            3: [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            4: [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42],
            5: [41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66,
                67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92,
                93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114,
                115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135,
                136, 137, 138, 139],
            6: [51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62],
            7: [61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74],
            8: [71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94],
            9: [81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94],
            10: [140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159,
                 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174],
            11: [171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190,
                 191, 192, 193, 194, 195, 196, 197, 198, 199, 200],
            12: [181, 182, 183, 184, 185, 186, 187, 188],
            13: [191, 192, 193, 194, 195, 196, 197, 198, 199, 200],
            14: [195, 196, 197, 198, 199]
        }
        self.persons = [

            "Payton Leon",
            "Elyse Lopez",
            "Zaire Blair",
            "Scarlett Wolfe",
            "Juan Mcpherson",
            "Dustin Salazar",
            "Harrison Valentine",
            "Esther Allen",
            "Lucille Morse",
            "Hugo Gross",
            "Danielle Arellano",
            "Erin Patel",
            "Malcolm Nunez",
            "Rowan Spears",
            "Yoselin Boone",
            "Carina Hooper",
            "Leonidas Yu",
            "Abril Mullen",
            "Skyler Willis",
            "Jaidyn Weaver",
            "Carla Burke",
            "Yasmin Riddle",
            "Shayla Hahn",
            "Bridget Clayton",
            "Aron Martin",
            "Raphael Cameron",
            "Brenden Robbins",
            "Emmanuel Dawson",
            "William Hurst",
            "Lana Ritter",
            "Caylee Mckenzie",
            "Carleigh Pennington",
            "Fernando Livingston",
            "Frida Hutchinson",
            "Wesley Huffman",
            "Elliott Burnett",
            "Brayan Moss",
            "Arielle Mcbride",
            "Henry Elliott",
            "Nico Mclean",
            "Coby Moran",
            "Reuben Walls",
            "Xiomara Payne",
            "Madison Houston",
            "Bethany Macdonald",
            "Nayeli Andrews",
            "Maddox Stone",
            "Ayla Ramos",
            "Jayla Rush",
            "Miya Archer",
            "Joaquin Knight",
            "Stella Kirk",
            "Laurel Evans",
            "Hudson Nixon",
            "Mckinley Galvan",
            "Jamison King",
            "Jaylin Everett",
            "Tomas Parrish",
            "Konner Oneill",
            "John Velazquez",
            "Joey Frost",
            "Maryjane Roth",
            "Jocelyn Charles",
            "Cloe Randall",
            "Cayden Hicks",
            "Addison Benton",
            "Marques Webster",
            "Belen Massey",
            "Rachel Henry",
            "Valentina Mccann",
            "Beau Rivas",
            "Helen Chandler",
            "Tiara Chapman",
            "Khalil Leach",
            "Kenya Shelton",
            "Harry Braun",
            "Sloane Lara",
            "Clinton Santos",
            "Joslyn Ponce",
            "Ada Donovan",
            "Johnathon Cline",
            "Aidan Morgan",
            "Elianna Riggs",
            "Quintin Powell",
            "Markus Hensley",
            "Kaylin Price",
            "Jazlynn Mccullough",
            "Zaniyah Thomas",
            "Dante Schneider",
            "Javion Hampton",
            "Nadia Solomon",
            "Cristopher Mckay",
            "Abbey Combs",
            "Yurem Perez",
            "Easton Arnold",
            "Alondra Bradley",
            "James Shannon",
            "Emiliano Larson",
            "Ainsley Garner",
            "Izabella Scott",
            "Mckenna Wiley",
            "Antwan Galloway",
            "Enzo Ramirez",
            "Giovanny Bridges",
            "Janae Glover",
            "Barrett Bonilla",
            "Aimee Crane",
            "Jerimiah Mcmahon",
            "Taryn Burton",
            "Nicholas Rodgers",
            "Jameson Hammond",
            "Tobias Sherman",
            "Dorian Hart",
            "Monique Chan",
            "Christian Carson",
            "Giovanni Dorsey",
            "Patrick Nielsen",
            "Yusuf Terrell",
            "Zayden Beard",
            "Mitchell Snyder",
            "Ramon Hudson",
            "Gilberto Pitts",
            "Kyan Mayer",
            "Peter Duffy",
            "Kaleb Martinez",
            "Hazel Vincent",
            "Brianna Fox",
            "Hailee Berger",
            "Brooklynn Hendricks",
            "Matthew Tate",
            "Chase Perry",
            "Harley Navarro",
            "Ximena Kidd",
            "Aaden Christensen",
            "Areli Irwin",
            "Adan Ayala",
            "Mike Rios",
            "Kameron Henderson",
            "Olive Moses",
            "Lilyana Lang",
            "Alina Salinas",
            "Sofia Poole",
            "Hanna Gaines",
            "Lucy Donaldson",
            "Lyla Munoz",
            "Aubrey Bennett",
            "Jaden Kent",
            "Mary Mayo",
            "Clayton Keller",
            "Kylan Bass",
            "Kenneth Petersen",
            "Leroy Gates",
            "Briana Mcintyre",
            "Sarah Gregory",
            "Amir Singh",
            "Jeremy Summers",
            "Keagan Weiss",
            "Rylee Ochoa",
            "Cesar Zamora",
            "Isabella Edwards",
            "Abigail Fuentes",
            "Ava Higgins",
            "Sarahi Lynn",
            "Perla Cochran",
            "Ricky Cantu",
            "Raquel Sanford",
            "Charlie Vargas",
            "Kendra Lamb",
            "Chris Roberson",
            "Erika Hansen",
            "Dillon Key",
            "Madelynn Garrison",
            "Beatrice Meadows",
            "Valery House",
            "Jessica Mcneil",
            "Magdalena Jefferson",
            "Adrienne Fuller",
            "Lawson Faulkner",
            "Liliana Becker",
            "Bryanna Strickland",
            "Allan Stevenson",
            "Camille Mcfarland",
            "Alannah Mathis",
            "Octavio Dyer",
            "Everett Holder",
            "Eric Kramer",
            "Cyrus Bender",
            "Maddison Richmond",
            "Jayvon Finley",
            "Asher Griffith",
            "Reese Logan",
            "Alani Gilmore",
            "Angelina Kemp",
            "Dixie Banks",
            "Dayanara Best",
            "Kaylah Williamson",
            "Alejandra Mcknight",
            "Mireya Cuevas",
            "Jesse Le",
            "Chana Sweeney"
        ]

    def test_partition_simple(self):

        community = {
            0: [0, 5, 10],
            1: [1, 2, 3, 4, 6, 7],
            2: [8, 9]
        }
        persons = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
        assert len(persons) == 11
        tables, persons, is_final = partition(community, str(uuid.uuid4()), persons, 3, {0: 1, 1: 1, 2:1})

        resulting_groups = [values for values in tables.values()]
        print(resulting_groups)

        self.assertTrue([0, 5, 10] in resulting_groups)
        self.assertTrue([1, 2, 3] in resulting_groups)
        self.assertTrue([4, 6, 7] in resulting_groups)
        self.assertTrue([8, 9] in resulting_groups)

    def test_partition_grouped(self):

        community = {
            0: [0, 5, 10],
            1: [1, 2, 3, 4, 6, 9, 10],
            2: [7, 8, 9]
        }
        persons = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
        assert len(persons) == 11
        tables, persons, is_final = partition(community, str(uuid.uuid4()), persons, 3, {0: 1, 1: 1, 2:1})

        resulting_groups = [sorted(values) for values in tables.values()]
        print(resulting_groups)

        # these are not the only right answers, there can be other right ones
        self.assertTrue([0, 5, 10] in resulting_groups)
        self.assertTrue([1, 2, 3] in resulting_groups)
        self.assertTrue([4, 6] in resulting_groups)
        self.assertTrue([7, 8, 9] in resulting_groups)

    def test_partition_with_one_column_of_clique_weight_zero(self):

        community = {
            0: [0, 1, 2],
            1: [3, 4, 5],
            2: [6, 7, 8, 9]
        }
        persons = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        assert len(persons) == 10
        tables, persons, is_final = partition(community, str(uuid.uuid4()), persons, 5, {0: 1, 1: 1, 2:0})

        self.assertTrue(is_final)

        resulting_groups = [sorted(values) for values in tables.values()]

        # these are not the only right answers, there can be other right ones
        self.assertTrue([0, 1, 2, 6, 7] in resulting_groups)
        self.assertTrue([3, 4, 5, 8, 9] in resulting_groups)

    def test_partition_with_one_column_of_clique_weight_zero_can_be_isolated(self):

        community = {
            0: [0, 1, 2],
            1: [3, 4, 5],
            2: [6, 7]
        }
        persons = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        assert len(persons) == 8
        tables, persons, is_final = partition(community, str(uuid.uuid4()), persons, 4, {0: 1, 1: 1, 2:0})

        resulting_groups = [sorted(values) for values in tables.values()]

        self.assertTrue(is_final)

        print(resulting_groups)
        # these are not the only right answers, there can be other right ones
        self.assertTrue([0, 1, 2, 7] in resulting_groups)
        self.assertTrue([3, 4, 5, 6] in resulting_groups)
