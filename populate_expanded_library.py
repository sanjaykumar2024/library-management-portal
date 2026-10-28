import os
import sys
import uuid
import re
import hashlib
from decimal import Decimal
from pathlib import Path

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from catalog.models import Book, BookCopy, Author, Category, EBookMetadata, BookReview
from catalog.cover_generator import BookCoverGenerator
from ebooks.kaggle_service import KaggleEBookService

NEW_BOOKS_CATALOG = [
    # ── TECHNOLOGY & DEVOPS ──
    {
        'title': 'Clean Architecture: A Craftsman\'s Guide to Software Structure and Design',
        'subtitle': 'A Craftsman\'s Guide to Software Structure and Design',
        'authors': ['Robert C. Martin'],
        'category': 'Technology',
        'publisher': 'Prentice Hall',
        'year': 2017,
        'pages': 432,
        'isbn': '9780134494166',
        'rating': 4.7,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'By applying universal rules of software architecture, you can dramatically improve developer productivity throughout the life of any software system. Now, building upon the success of his best-selling books Clean Code and The Clean Coder, legendary software craftsman Robert C. Martin reveals those rules and helps you apply them.',
        'copies': 3,
        'shelf_prefix': 'Stack TECH, Row 1, Shelf'
    },
    {
        'title': 'The Phoenix Project: A Novel about IT, DevOps, and Helping Your Business Win',
        'subtitle': 'A Novel about IT, DevOps, and Helping Your Business Win',
        'authors': ['Gene Kim', 'Kevin Behr', 'George Spafford'],
        'category': 'Technology',
        'publisher': 'IT Revolution Press',
        'year': 2013,
        'pages': 382,
        'isbn': '9780988262591',
        'rating': 4.8,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Bill, an IT manager at Parts Unlimited, has been tasked with the impossible: rescue an over-budget, behind-schedule mission-critical project code-named Phoenix. With the company\'s survival at stake, Bill must revolutionize IT workflows, continuous integration, and operations using modern DevOps principles.',
        'copies': 3,
        'shelf_prefix': 'Stack TECH, Row 2, Shelf'
    },
    {
        'title': 'Kubernetes: Up and Running: Dive into the Future of Infrastructure',
        'subtitle': 'Dive into the Future of Infrastructure',
        'authors': ['Brendan Burns', 'Joe Beda', 'Kelsey Hightower'],
        'category': 'Technology',
        'publisher': 'O\'Reilly Media',
        'year': 2022,
        'pages': 340,
        'isbn': '9781098110208',
        'rating': 4.7,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Legendary cloud native pioneers Brendan Burns, Joe Beda, and Kelsey Hightower explain how Kubernetes and container technology can help you achieve new levels of velocity, agility, reliability, and efficiency in distributed microservice deployments.',
        'copies': 2,
        'shelf_prefix': 'Stack TECH, Row 3, Shelf'
    },
    {
        'title': 'Designing Distributed Systems: Patterns and Paradigms for Scalable, Reliable Services',
        'subtitle': 'Patterns and Paradigms for Scalable, Reliable Services',
        'authors': ['Brendan Burns'],
        'category': 'Technology',
        'publisher': 'O\'Reilly Media',
        'year': 2018,
        'pages': 166,
        'isbn': '9781491983645',
        'rating': 4.6,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Without established patterns of distributed systems development, developers often end up reinventing the wheel. This practical book presents a collection of repeatable, generic patterns to make the development of reliable distributed systems far more approachable and efficient.',
        'copies': 2,
        'shelf_prefix': 'Stack TECH, Row 3, Shelf'
    },
    {
        'title': 'System Design Interview: An Insider\'s Guide',
        'subtitle': 'An Insider\'s Guide to Large-Scale Distributed Architecture',
        'authors': ['Alex Xu'],
        'category': 'Technology',
        'publisher': 'ByteDance Press',
        'year': 2020,
        'pages': 300,
        'isbn': '9781736049112',
        'rating': 4.9,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'An indispensable guide to mastering large-scale distributed systems architecture, covering rate limiters, key-value stores, distributed message queues, web crawlers, real-time notification systems, and global chat backends.',
        'copies': 3,
        'shelf_prefix': 'Stack TECH, Row 4, Shelf'
    },
    {
        'title': 'The DevOps Handbook: How to Create World-Class Agility, Reliability, and Security',
        'subtitle': 'How to Create World-Class Agility, Reliability, and Security',
        'authors': ['Gene Kim', 'Jez Humble', 'Patrick Debois', 'John Willis'],
        'category': 'Technology',
        'publisher': 'IT Revolution Press',
        'year': 2016,
        'pages': 480,
        'isbn': '9781942788003',
        'rating': 4.7,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'For decades, technology leaders have struggled to balance agility, reliability, and security. The DevOps Handbook provides concrete architectural roadmaps, automated CI/CD patterns, and organizational culture transformations to achieve continuous delivery.',
        'copies': 2,
        'shelf_prefix': 'Stack TECH, Row 4, Shelf'
    },
    {
        'title': 'Chip War: The Fight for the World\'s Most Critical Technology',
        'subtitle': 'The Fight for the World\'s Most Critical Technology',
        'authors': ['Chris Miller'],
        'category': 'Technology',
        'publisher': 'Scribner',
        'year': 2022,
        'pages': 464,
        'isbn': '9781982172008',
        'rating': 4.8,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Financial Times Business Book of the Year. An illuminating history of how microchips became the new oil—the scarce resource modern civilization depends on—and the fierce geopolitical battle to control semiconductor manufacturing.',
        'copies': 3,
        'shelf_prefix': 'Stack TECH, Row 5, Shelf'
    },

    # ── COMPUTER SCIENCE ──
    {
        'title': 'The Art of Computer Programming, Volume 1: Fundamental Algorithms',
        'subtitle': 'Fundamental Algorithms (3rd Edition)',
        'authors': ['Donald E. Knuth'],
        'category': 'Computer Science',
        'publisher': 'Addison-Wesley Professional',
        'year': 1997,
        'pages': 672,
        'isbn': '9780201896831',
        'rating': 4.9,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'The bible of computer science. Professor Donald Knuth\'s monumental masterwork introduces fundamental mathematical preliminaries, algorithmic notation, data structures, trees, dynamic storage allocation, and information manipulation.',
        'copies': 2,
        'shelf_prefix': 'Stack CS, Row 1, Shelf'
    },
    {
        'title': 'Compilers: Principles, Techniques, and Tools',
        'subtitle': 'The Definitive Dragon Book',
        'authors': ['Alfred V. Aho', 'Monica S. Lam', 'Ravi Sethi', 'Jeffrey D. Ullman'],
        'category': 'Computer Science',
        'publisher': 'Pearson',
        'year': 2006,
        'pages': 1040,
        'isbn': '9780321486813',
        'rating': 4.8,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Known affectionately to software engineers worldwide as the Dragon Book, this definitive text covers lexical analysis, syntax-directed translation, intermediate code generation, runtime environments, and modern optimization techniques.',
        'copies': 2,
        'shelf_prefix': 'Stack CS, Row 2, Shelf'
    },
    {
        'title': 'Operating Systems: Three Easy Pieces',
        'subtitle': 'Virtualization, Concurrency, and Persistence',
        'authors': ['Remzi H. Arpaci-Dusseau', 'Andrea C. Arpaci-Dusseau'],
        'category': 'Computer Science',
        'publisher': 'Arpaci-Dusseau Books',
        'year': 2018,
        'pages': 714,
        'isbn': '9781985086593',
        'rating': 4.9,
        'rights_status': 'OPEN_LICENSE',
        'description': 'A beloved, crystal-clear textbook covering the foundational pillars of modern operating systems: CPU and memory virtualization, multi-threaded concurrency synchronization, and durable file system persistence.',
        'copies': 3,
        'shelf_prefix': 'Stack CS, Row 2, Shelf'
    },
    {
        'title': 'Computer Systems: A Programmer\'s Perspective',
        'subtitle': 'CS:APP (3rd Edition)',
        'authors': ['Randal E. Bryant', 'David R. O\'Hallaron'],
        'category': 'Computer Science',
        'publisher': 'Pearson',
        'year': 2015,
        'pages': 1152,
        'isbn': '9780134092669',
        'rating': 4.9,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'By explaining how assembly code executes on hardware, how linkers resolve references, how caches optimize latency, and how virtual memory isolates processes, CS:APP bridges the gap between hardware architecture and high-performance software.',
        'copies': 2,
        'shelf_prefix': 'Stack CS, Row 3, Shelf'
    },
    {
        'title': 'Introduction to the Theory of Computation',
        'subtitle': 'Formal Languages, Automata, and Complexity',
        'authors': ['Michael Sipser'],
        'category': 'Computer Science',
        'publisher': 'Cengage Learning',
        'year': 2012,
        'pages': 504,
        'isbn': '9781133187790',
        'rating': 4.8,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'The most celebrated theoretical computer science text. Michael Sipser presents automata theory, regular expressions, context-free grammars, Turing machines, computability, and NP-completeness with unmatched pedagogical elegance.',
        'copies': 2,
        'shelf_prefix': 'Stack CS, Row 4, Shelf'
    },
    {
        'title': 'Database System Concepts',
        'subtitle': 'The Complete Database Architecture Guide',
        'authors': ['Abraham Silberschatz', 'Henry F. Korth', 'S. Sudarshan'],
        'category': 'Computer Science',
        'publisher': 'McGraw-Hill Education',
        'year': 2019,
        'pages': 1376,
        'isbn': '9780078022159',
        'rating': 4.7,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'The premier academic standard on relational database engines, indexing structures (B+ trees, LSM trees), SQL query optimization, ACID concurrency control, write-ahead logging, and distributed transactions.',
        'copies': 3,
        'shelf_prefix': 'Stack CS, Row 4, Shelf'
    },
    {
        'title': 'The Mythical Man-Month: Essays on Software Engineering',
        'subtitle': 'Anniversary Edition',
        'authors': ['Frederick P. Brooks Jr.'],
        'category': 'Computer Science',
        'publisher': 'Addison-Wesley Professional',
        'year': 1995,
        'pages': 336,
        'isbn': '9780201835953',
        'rating': 4.8,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Few books on software project management have been as influential and enduring. Fred Brooks reveals timeless software truths, including Brooks\'s Law: "Adding manpower to a late software project makes it later."',
        'copies': 3,
        'shelf_prefix': 'Stack CS, Row 5, Shelf'
    },
    {
        'title': 'Deep Learning with Python',
        'subtitle': 'Practical Neural Networks with Keras and PyTorch',
        'authors': ['François Chollet'],
        'category': 'Computer Science',
        'publisher': 'Manning Publications',
        'year': 2021,
        'pages': 504,
        'isbn': '9781617296864',
        'rating': 4.9,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Written by Keras creator François Chollet, this book introduces the field of deep learning using Python and the powerful Keras and TensorFlow frameworks. It features intuitive explanations and zero mathematical obfuscation.',
        'copies': 3,
        'shelf_prefix': 'Stack CS, Row 5, Shelf'
    },

    # ── SCIENCE FICTION & SPECULATIVE ──
    {
        'title': 'Project Hail Mary',
        'subtitle': 'A Novel',
        'authors': ['Andy Weir'],
        'category': 'Science Fiction',
        'publisher': 'Ballantine Books',
        'year': 2021,
        'pages': 496,
        'isbn': '9780593135204',
        'rating': 4.9,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Ryland Grace is the sole survivor on a desperate, last-chance mission to save humanity from an interstellar extinction event. He just has to figure out who he is, remember his scientific training, and collaborate with an unexpected ally.',
        'copies': 3,
        'shelf_prefix': 'Stack SF, Row 1, Shelf'
    },
    {
        'title': 'The Martian',
        'subtitle': 'A Novel',
        'authors': ['Andy Weir'],
        'category': 'Science Fiction',
        'publisher': 'Crown Publishing',
        'year': 2014,
        'pages': 384,
        'isbn': '9780804139021',
        'rating': 4.8,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Six days ago, astronaut Mark Watney became one of the first people to walk on Mars. Now, he is stranded alone on the hostile Martian surface after a dust storm forces his crew to evacuate. Armed only with his ingenuity and engineering skills, he must survive.',
        'copies': 3,
        'shelf_prefix': 'Stack SF, Row 1, Shelf'
    },
    {
        'title': 'Rendezvous with Rama',
        'subtitle': 'Rama Series Book 1',
        'authors': ['Arthur C. Clarke'],
        'category': 'Science Fiction',
        'publisher': 'Gollancz',
        'year': 1973,
        'pages': 256,
        'isbn': '9780575077331',
        'rating': 4.7,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'A massive cylindrical alien vessel enters the solar system in the twenty-second century. A team of human astronauts is dispatched to explore the enigmatic, spinning world within world, uncovering awe-inspiring extraterrestrial artifacts.',
        'copies': 2,
        'shelf_prefix': 'Stack SF, Row 2, Shelf'
    },
    {
        'title': 'Contact',
        'subtitle': 'A Novel',
        'authors': ['Carl Sagan'],
        'category': 'Science Fiction',
        'publisher': 'Simon & Schuster',
        'year': 1985,
        'pages': 448,
        'isbn': '9780671434007',
        'rating': 4.8,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Astronomer Ellie Arroway discovers the first confirmed extraterrestrial transmission from the Vega system, carrying plans for a mysterious machine that will carry a human voyager across the fabric of spacetime.',
        'copies': 2,
        'shelf_prefix': 'Stack SF, Row 2, Shelf'
    },
    {
        'title': 'Children of Time',
        'subtitle': 'Children of Time Series Book 1',
        'authors': ['Adrian Tchaikovsky'],
        'category': 'Science Fiction',
        'publisher': 'Tor Books',
        'year': 2015,
        'pages': 608,
        'isbn': '9780316452502',
        'rating': 4.8,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Arthur C. Clarke Award Winner. A terraformed world seeded with an evolutionary virus fosters an advanced civilization of sentient arachnids, whose fate converges with the remnants of humanity fleeing a ruined Earth on an ark ship.',
        'copies': 3,
        'shelf_prefix': 'Stack SF, Row 3, Shelf'
    },
    {
        'title': 'The Forever War',
        'subtitle': 'The Hugo and Nebula Award-Winning Masterpiece',
        'authors': ['Joe Haldeman'],
        'category': 'Science Fiction',
        'publisher': 'St. Martin\'s Press',
        'year': 1974,
        'pages': 272,
        'isbn': '9780312536633',
        'rating': 4.7,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Private William Mandella is drafted into an interstellar war against an elusive alien race. But because of relativistic time dilation, every tour of duty takes months for him, while centuries pass on Earth.',
        'copies': 2,
        'shelf_prefix': 'Stack SF, Row 3, Shelf'
    },
    {
        'title': 'Station Eleven',
        'subtitle': 'A Novel',
        'authors': ['Emily St. John Mandel'],
        'category': 'Science Fiction',
        'publisher': 'Knopf',
        'year': 2014,
        'pages': 352,
        'isbn': '9780385353304',
        'rating': 4.6,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'National Book Award Finalist. In a post-pandemic North America where civilization has collapsed, a nomadic troupe of actors and musicians called The Traveling Symphony travels between settlements performing Shakespeare and music.',
        'copies': 2,
        'shelf_prefix': 'Stack SF, Row 4, Shelf'
    },
    {
        'title': 'Childhood\'s End',
        'subtitle': 'Arthur C. Clarke Science Fiction Classics',
        'authors': ['Arthur C. Clarke'],
        'category': 'Science Fiction',
        'publisher': 'Ballantine Books',
        'year': 1953,
        'pages': 224,
        'isbn': '9780345347954',
        'rating': 4.7,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Giant alien spaceships suddenly appear over Earth\'s major cities. Known as the Overlords, these peaceful beings end war, poverty, and disease—yet refuse to show themselves, leading humanity toward a transcendent and startling destiny.',
        'copies': 2,
        'shelf_prefix': 'Stack SF, Row 4, Shelf'
    },

    # ── LITERATURE & WORLD CLASSICS ──
    {
        'title': 'The Old Man and the Sea',
        'subtitle': 'Nobel Prize Winner in Literature',
        'authors': ['Ernest Hemingway'],
        'category': 'Literature',
        'publisher': 'Charles Scribner\'s Sons',
        'year': 1952,
        'pages': 128,
        'isbn': '9780684801223',
        'rating': 4.6,
        'rights_status': 'PUBLIC_DOMAIN',
        'description': 'Hemingway\'s immortal masterpiece of Santiago, an aging Cuban fisherman who struggles alone in the Gulf Stream against a giant marlin. An unforgettable testament to human courage, resilience, and endurance.',
        'copies': 3,
        'shelf_prefix': 'Stack LIT, Row 1, Shelf'
    },
    {
        'title': 'The Road',
        'subtitle': 'Pulitzer Prize Winner',
        'authors': ['Cormac McCarthy'],
        'category': 'Literature',
        'publisher': 'Alfred A. Knopf',
        'year': 2006,
        'pages': 287,
        'isbn': '9780307265432',
        'rating': 4.7,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'A father and his young son walk alone through burned America. Nothing moves in the ravaged landscape save the ash on the wind. They have nothing; just a pistol to defend themselves, the clothes they are wearing, and each other.',
        'copies': 3,
        'shelf_prefix': 'Stack LIT, Row 1, Shelf'
    },
    {
        'title': 'The Stranger',
        'subtitle': 'Vintage International Edition',
        'authors': ['Albert Camus'],
        'category': 'Literature',
        'publisher': 'Vintage Books',
        'year': 1942,
        'pages': 123,
        'isbn': '9780679720201',
        'rating': 4.6,
        'rights_status': 'PUBLIC_DOMAIN',
        'description': 'Through the story of an ordinary, detached man unwittingly drawn into a senseless murder on an Algerian beach, Camus explores what he termed "the nakedness of man faced with the absurd."',
        'copies': 3,
        'shelf_prefix': 'Stack LIT, Row 2, Shelf'
    },
    {
        'title': 'Catch-22',
        'subtitle': '50th Anniversary Edition',
        'authors': ['Joseph Heller'],
        'category': 'Literature',
        'publisher': 'Simon & Schuster',
        'year': 1961,
        'pages': 453,
        'isbn': '9781451626650',
        'rating': 4.7,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Set in Italy during World War II, this hilarious and profound satirical masterpiece chronicles the heroic struggles of Bombardier Yossarian to survive the bureaucratic lunacy of military command.',
        'copies': 2,
        'shelf_prefix': 'Stack LIT, Row 2, Shelf'
    },
    {
        'title': 'Slaughterhouse-Five',
        'subtitle': 'A Novel',
        'authors': ['Kurt Vonnegut'],
        'category': 'Literature',
        'publisher': 'Delacorte Press',
        'year': 1969,
        'pages': 275,
        'isbn': '9780385333849',
        'rating': 4.8,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Billy Pilgrim has come unstuck in time. Centered around the firebombing of Dresden, Vonnegut\'s anti-war classic combines biting dark humor, science fiction, and profound moral reflection.',
        'copies': 3,
        'shelf_prefix': 'Stack LIT, Row 3, Shelf'
    },
    {
        'title': 'Things Fall Apart',
        'subtitle': 'The African Trilogy Book 1',
        'authors': ['Chinua Achebe'],
        'category': 'Literature',
        'publisher': 'Heinemann',
        'year': 1958,
        'pages': 209,
        'isbn': '9780385474542',
        'rating': 4.7,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Achebe\'s seminal masterpiece portrays the tragic fall of Okonkwo, an Igbo warrior and leader in Nigeria, as European colonial administration and missionaries disrupt traditional society.',
        'copies': 3,
        'shelf_prefix': 'Stack LIT, Row 3, Shelf'
    },
    {
        'title': 'The Master and Margarita',
        'subtitle': 'Penguin Classics Deluxe Edition',
        'authors': ['Mikhail Bulgakov'],
        'category': 'Literature',
        'publisher': 'Penguin Books',
        'year': 1967,
        'pages': 412,
        'isbn': '9780143108276',
        'rating': 4.8,
        'rights_status': 'PUBLIC_DOMAIN',
        'description': 'A dazzling literary masterpiece of twentieth-century Russian literature. The devil, in the guise of Professor Woland, arrives in 1930s Moscow accompanied by a talking black cat with a penchant for vodka and chess.',
        'copies': 2,
        'shelf_prefix': 'Stack LIT, Row 4, Shelf'
    },
    {
        'title': 'Blindness',
        'subtitle': 'Nobel Prize Winner in Literature',
        'authors': ['José Saramago'],
        'category': 'Literature',
        'publisher': 'Harcourt',
        'year': 1995,
        'pages': 352,
        'isbn': '9780156007757',
        'rating': 4.7,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'A city is hit by an epidemic of "white blindness" that spares only one woman. A searing allegory of human resilience, civilization\'s fragility, and moral fortitude.',
        'copies': 2,
        'shelf_prefix': 'Stack LIT, Row 4, Shelf'
    },

    # ── HISTORY & CIVILIZATION ──
    {
        'title': 'SPQR: A History of Ancient Rome',
        'subtitle': 'A History of Ancient Rome',
        'authors': ['Mary Beard'],
        'category': 'History',
        'publisher': 'Liveright Publishing',
        'year': 2015,
        'pages': 608,
        'isbn': '9780871404237',
        'rating': 4.8,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'World-renowned Cambridge classicist Mary Beard explores how Rome grew from an obscure village into an undisputed global superpower, examining Roman democracy, slavery, warfare, citizenship, and power dynamics.',
        'copies': 3,
        'shelf_prefix': 'Stack HIST, Row 1, Shelf'
    },
    {
        'title': 'Team of Rivals: The Political Genius of Abraham Lincoln',
        'subtitle': 'The Political Genius of Abraham Lincoln',
        'authors': ['Doris Kearns Goodwin'],
        'category': 'History',
        'publisher': 'Simon & Schuster',
        'year': 2005,
        'pages': 944,
        'isbn': '9780684824901',
        'rating': 4.9,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Winner of the Lincoln Prize. A monumental biography focusing on Lincoln\'s brilliant political mastery in appointing his fiercest political rivals into his cabinet to preserve the American Union during the Civil War.',
        'copies': 2,
        'shelf_prefix': 'Stack HIST, Row 1, Shelf'
    },
    {
        'title': 'The Wright Brothers',
        'subtitle': 'The Dramatic Story of the Men Who Taught the World to Fly',
        'authors': ['David McCullough'],
        'category': 'History',
        'publisher': 'Simon & Schuster',
        'year': 2015,
        'pages': 336,
        'isbn': '9781476728742',
        'rating': 4.8,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Two-time Pulitzer Prize winner David McCullough tells the dramatic, inspiring story of Wilbur and Orville Wright, two courageous bicycle mechanics from Ohio who solved the mystery of powered human flight.',
        'copies': 2,
        'shelf_prefix': 'Stack HIST, Row 2, Shelf'
    },
    {
        'title': 'Churchill: A Life',
        'subtitle': 'The Definitive Biography',
        'authors': ['Martin Gilbert'],
        'category': 'History',
        'publisher': 'Henry Holt and Company',
        'year': 1991,
        'pages': 1088,
        'isbn': '9780805023961',
        'rating': 4.8,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'The definitive single-volume biography by Sir Winston Churchill\'s official biographer. Draws from private diaries, top-secret telegrams, and state archives to recount his leadership during World War II.',
        'copies': 2,
        'shelf_prefix': 'Stack HIST, Row 2, Shelf'
    },
    {
        'title': 'Genghis Khan and the Making of the Modern World',
        'subtitle': 'The Making of the Modern World',
        'authors': ['Jack Weatherford'],
        'category': 'History',
        'publisher': 'Crown',
        'year': 2004,
        'pages': 352,
        'isbn': '9780609809648',
        'rating': 4.7,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'An astonishing revisionist history showing how the Mongol empire under Genghis Khan introduced paper currency, religious tolerance, diplomatic immunity, and unified global trade routes across Eurasia.',
        'copies': 2,
        'shelf_prefix': 'Stack HIST, Row 3, Shelf'
    },
    {
        'title': 'Alexander Hamilton',
        'subtitle': 'The Definitive Biography',
        'authors': ['Ron Chernow'],
        'category': 'History',
        'publisher': 'Penguin Press',
        'year': 2004,
        'pages': 832,
        'isbn': '9780143034759',
        'rating': 4.9,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'The New York Times bestseller that inspired the smash hit musical. Ron Chernow presents the gripping biography of an illegitimate Caribbean orphan who became George Washington\'s right hand and the architect of American capitalism.',
        'copies': 2,
        'shelf_prefix': 'Stack HIST, Row 3, Shelf'
    },
    {
        'title': 'The Crusades: The Authoritative History of the War for the Holy Land',
        'subtitle': 'The War for the Holy Land',
        'authors': ['Thomas Asbridge'],
        'category': 'History',
        'publisher': 'Ecco',
        'year': 2010,
        'pages': 784,
        'isbn': '9780060787288',
        'rating': 4.7,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'A monumental, balanced, and gripping history of the centuries-long conflict between Christians and Muslims for control of Jerusalem and the Near East, told through both Western and Islamic contemporary sources.',
        'copies': 2,
        'shelf_prefix': 'Stack HIST, Row 4, Shelf'
    },
    {
        'title': 'Postwar: A History of Europe Since 1945',
        'subtitle': 'A History of Europe Since 1945',
        'authors': ['Tony Judt'],
        'category': 'History',
        'publisher': 'Penguin Press',
        'year': 2005,
        'pages': 933,
        'isbn': '9780143037750',
        'rating': 4.9,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Pulitzer Prize Finalist. An unparalleled, sweeping account of how Europe recovered from the catastrophic destruction of World War II to rebuild its democratic institutions, welfare states, and supranational unity.',
        'copies': 2,
        'shelf_prefix': 'Stack HIST, Row 4, Shelf'
    },

    # ── PHILOSOPHY ──
    {
        'title': 'Nicomachean Ethics',
        'subtitle': 'Aristotle\'s Classical Moral Philosophy',
        'authors': ['Aristotle'],
        'category': 'Philosophy',
        'publisher': 'Oxford World\'s Classics',
        'year': 350,
        'pages': 336,
        'isbn': '9780199213610',
        'rating': 4.8,
        'rights_status': 'PUBLIC_DOMAIN',
        'description': 'Aristotle explores eudaimonia (human flourishing) and the nature of moral virtue, defining virtue as the golden mean between excess and deficiency in human actions and emotions.',
        'copies': 3,
        'shelf_prefix': 'Stack PHIL, Row 1, Shelf'
    },
    {
        'title': 'Letters from a Stoic',
        'subtitle': 'Epistulae Morales ad Lucilium',
        'authors': ['Lucius Annaeus Seneca'],
        'category': 'Philosophy',
        'publisher': 'Penguin Classics',
        'year': 65,
        'pages': 256,
        'isbn': '9780140442106',
        'rating': 4.9,
        'rights_status': 'PUBLIC_DOMAIN',
        'description': 'Seneca offers practical, timeless advice on overcoming fear, bearing adversity with dignity, valuing true friendship, mastering time, and finding tranquility amidst imperial chaos.',
        'copies': 3,
        'shelf_prefix': 'Stack PHIL, Row 1, Shelf'
    },
    {
        'title': 'Critique of Pure Reason',
        'subtitle': 'The Foundational Masterwork of Modern Epistemology',
        'authors': ['Immanuel Kant'],
        'category': 'Philosophy',
        'publisher': 'Cambridge University Press',
        'year': 1781,
        'pages': 784,
        'isbn': '9780521657297',
        'rating': 4.7,
        'rights_status': 'PUBLIC_DOMAIN',
        'description': 'Kant synthesizes rationalism and empiricism, establishing synthetic a priori judgments and investigating the conditions of possible experience through space, time, and transcendental categories.',
        'copies': 2,
        'shelf_prefix': 'Stack PHIL, Row 2, Shelf'
    },
    {
        'title': 'Thus Spoke Zarathustra',
        'subtitle': 'A Book for All and None',
        'authors': ['Friedrich Nietzsche'],
        'category': 'Philosophy',
        'publisher': 'Penguin Classics',
        'year': 1883,
        'pages': 352,
        'isbn': '9780140441185',
        'rating': 4.8,
        'rights_status': 'PUBLIC_DOMAIN',
        'description': 'Nietzsche\'s philosophical poem introducing the Übermensch, the Will to Power, and the Eternal Recurrence through the visionary prophet Zarathustra descending from his mountain retreat.',
        'copies': 3,
        'shelf_prefix': 'Stack PHIL, Row 2, Shelf'
    },
    {
        'title': 'Discourse on Method and Meditations on First Philosophy',
        'subtitle': 'Foundations of Modern Rationalism',
        'authors': ['René Descartes'],
        'category': 'Philosophy',
        'publisher': 'Hackett Publishing',
        'year': 1637,
        'pages': 160,
        'isbn': '9780872204201',
        'rating': 4.7,
        'rights_status': 'PUBLIC_DOMAIN',
        'description': 'Descartes lays down radical skepticism and arrives at the indubitable foundation of all knowledge: Cogito, ergo sum ("I think, therefore I am"), establishing Cartesian dualism.',
        'copies': 2,
        'shelf_prefix': 'Stack PHIL, Row 3, Shelf'
    },
    {
        'title': 'The Myth of Sisyphus',
        'subtitle': 'An Essay on the Absurd',
        'authors': ['Albert Camus'],
        'category': 'Philosophy',
        'publisher': 'Vintage International',
        'year': 1942,
        'pages': 212,
        'isbn': '9780679733737',
        'rating': 4.8,
        'rights_status': 'PUBLIC_DOMAIN',
        'description': 'Camus confronts the ultimate philosophical question: does the absurdity of existence require suicide? His defiant conclusion: one must imagine Sisyphus happy as he pushes his rock up the mountain.',
        'copies': 3,
        'shelf_prefix': 'Stack PHIL, Row 3, Shelf'
    },
    {
        'title': 'Existentialism Is a Humanism',
        'subtitle': 'Including a Commentary on The Stranger',
        'authors': ['Jean-Paul Sartre'],
        'category': 'Philosophy',
        'publisher': 'Yale University Press',
        'year': 1946,
        'pages': 128,
        'isbn': '9780300115468',
        'rating': 4.6,
        'rights_status': 'PUBLIC_DOMAIN',
        'description': 'Sartre\'s clearest and most accessible defense of existentialist ethics: existence precedes essence, meaning humans are condemned to be free and must actively define their own values.',
        'copies': 2,
        'shelf_prefix': 'Stack PHIL, Row 4, Shelf'
    },

    # ── PSYCHOLOGY & COGNITIVE SCIENCE ──
    {
        'title': 'Predictably Irrational: The Hidden Forces That Shape Our Decisions',
        'subtitle': 'The Hidden Forces That Shape Our Decisions',
        'authors': ['Dan Ariely'],
        'category': 'Psychology',
        'publisher': 'HarperCollins',
        'year': 2008,
        'pages': 384,
        'isbn': '9780061353246',
        'rating': 4.7,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'MIT behavioral economist Dan Ariely refutes the common assumption that we behave in fundamentally rational ways. Through entertaining experiments, he shows systematic errors in our thinking.',
        'copies': 3,
        'shelf_prefix': 'Stack PSYCH, Row 1, Shelf'
    },
    {
        'title': 'The Power of Habit: Why We Do What We Do in Life and Business',
        'subtitle': 'Why We Do What We Do in Life and Business',
        'authors': ['Charles Duhigg'],
        'category': 'Psychology',
        'publisher': 'Random House',
        'year': 2012,
        'pages': 416,
        'isbn': '9780812981605',
        'rating': 4.8,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Award-winning New York Times reporter Charles Duhigg explains the neurological habit loop (cue, routine, reward) and reveals how individuals and organizations can transform their lives by altering keystone habits.',
        'copies': 3,
        'shelf_prefix': 'Stack PSYCH, Row 1, Shelf'
    },
    {
        'title': 'Blink: The Power of Thinking Without Thinking',
        'subtitle': 'The Power of Thinking Without Thinking',
        'authors': ['Malcolm Gladwell'],
        'category': 'Psychology',
        'publisher': 'Little, Brown and Company',
        'year': 2005,
        'pages': 320,
        'isbn': '9780316010665',
        'rating': 4.6,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'An examination of the instant judgments we make in the blink of an eye—how expert "thin-slicing" works, why snap decisions can be astonishingly accurate, and when subconscious biases mislead us.',
        'copies': 3,
        'shelf_prefix': 'Stack PSYCH, Row 2, Shelf'
    },
    {
        'title': 'Drive: The Surprising Truth About What Motivates Us',
        'subtitle': 'The Surprising Truth About What Motivates Us',
        'authors': ['Daniel H. Pink'],
        'category': 'Psychology',
        'publisher': 'Riverhead Books',
        'year': 2009,
        'pages': 256,
        'isbn': '9781594488849',
        'rating': 4.7,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Forget carrots and sticks. Daniel Pink exposes the mismatch between what science knows and what business does, proving that high performance is driven by autonomy, mastery, and purpose.',
        'copies': 2,
        'shelf_prefix': 'Stack PSYCH, Row 2, Shelf'
    },
    {
        'title': 'The Man Who Mistook His Wife for a Hat',
        'subtitle': 'And Other Clinical Tales',
        'authors': ['Oliver Sacks'],
        'category': 'Psychology',
        'publisher': 'Summit Books',
        'year': 1985,
        'pages': 243,
        'isbn': '9780684853949',
        'rating': 4.8,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Neurologist Oliver Sacks recounts fascinating, compassionate clinical case studies of patients navigating profound neurological disorders, agnosias, phantom limbs, and Tourette\'s syndrome.',
        'copies': 2,
        'shelf_prefix': 'Stack PSYCH, Row 3, Shelf'
    },
    {
        'title': 'Behave: The Biology of Humans at Our Best and Worst',
        'subtitle': 'The Biology of Humans at Our Best and Worst',
        'authors': ['Robert M. Sapolsky'],
        'category': 'Psychology',
        'publisher': 'Penguin Press',
        'year': 2017,
        'pages': 800,
        'isbn': '9781594204555',
        'rating': 4.9,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Stanford neurobiologist Robert Sapolsky delivers a monumental investigation into why humans act the way they do, tracing neurochemical impulses seconds before action back to evolutionary pressures over millennia.',
        'copies': 2,
        'shelf_prefix': 'Stack PSYCH, Row 3, Shelf'
    },
    {
        'title': 'Stumbling on Happiness',
        'subtitle': 'A Journey into Prospective Cognition',
        'authors': ['Daniel Gilbert'],
        'category': 'Psychology',
        'publisher': 'Knopf',
        'year': 2006,
        'pages': 336,
        'isbn': '9781400042661',
        'rating': 4.6,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Harvard psychologist Daniel Gilbert reveals why human imagination struggles to accurately forecast what will make us happy in the future, using witty analogies and cutting-edge cognitive experiments.',
        'copies': 2,
        'shelf_prefix': 'Stack PSYCH, Row 4, Shelf'
    },

    # ── BUSINESS & ECONOMICS ──
    {
        'title': 'The Innovator\'s Dilemma: When New Technologies Cause Great Firms to Fail',
        'subtitle': 'When New Technologies Cause Great Firms to Fail',
        'authors': ['Clayton M. Christensen'],
        'category': 'Business & Economics',
        'publisher': 'Harvard Business Review Press',
        'year': 1997,
        'pages': 286,
        'isbn': '9781633691780',
        'rating': 4.8,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'One of the most influential business books ever written. Harvard professor Clayton Christensen outlines disruptive innovation and why market-leading companies often fail precisely by doing everything right.',
        'copies': 3,
        'shelf_prefix': 'Stack BIZ, Row 1, Shelf'
    },
    {
        'title': 'Thinking in Bets: Making Smarter Decisions When You Don\'t Have All the Facts',
        'subtitle': 'Making Smarter Decisions When You Don\'t Have All the Facts',
        'authors': ['Annie Duke'],
        'category': 'Business & Economics',
        'publisher': 'Portfolio',
        'year': 2018,
        'pages': 288,
        'isbn': '9780735216358',
        'rating': 4.7,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'World Series of Poker champion turned business consultant Annie Duke shows how to decouple decision quality from outcomes, combat cognitive biases, and make smarter strategic bets under deep uncertainty.',
        'copies': 3,
        'shelf_prefix': 'Stack BIZ, Row 1, Shelf'
    },
    {
        'title': 'The Hard Thing About Hard Things: Building a Business When There Are No Easy Answers',
        'subtitle': 'Building a Business When There Are No Easy Answers',
        'authors': ['Ben Horowitz'],
        'category': 'Business & Economics',
        'publisher': 'HarperBusiness',
        'year': 2014,
        'pages': 304,
        'isbn': '9780062273208',
        'rating': 4.9,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Andreessen Horowitz co-founder Ben Horowitz shares brutal, unvarnished wisdom on managing startups through crises, firing friends, poaching executives, and leading when catastrophe strikes.',
        'copies': 3,
        'shelf_prefix': 'Stack BIZ, Row 2, Shelf'
    },
    {
        'title': 'Capital in the Twenty-First Century',
        'subtitle': 'A Global Analysis of Wealth and Inequality',
        'authors': ['Thomas Piketty'],
        'category': 'Business & Economics',
        'publisher': 'Belknap Press',
        'year': 2014,
        'pages': 696,
        'isbn': '9780674430006',
        'rating': 4.7,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'An international sensation. French economist Thomas Piketty analyzes historic wealth distribution data across three centuries, showing that whenever return on capital exceeds economic growth (r > g), inequality widens.',
        'copies': 2,
        'shelf_prefix': 'Stack BIZ, Row 2, Shelf'
    },
    {
        'title': 'Liar\'s Poker: Rising Through the Wreckage on Wall Street',
        'subtitle': 'Rising Through the Wreckage on Wall Street',
        'authors': ['Michael Lewis'],
        'category': 'Business & Economics',
        'publisher': 'W. W. Norton & Company',
        'year': 1989,
        'pages': 310,
        'isbn': '9780393027501',
        'rating': 4.8,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Michael Lewis\'s riotous insider tell-all of Salomon Brothers trading desks during the wild 1980s bond market boom, capturing greed, ambition, and financial engineering in vivid detail.',
        'copies': 2,
        'shelf_prefix': 'Stack BIZ, Row 3, Shelf'
    },
    {
        'title': 'Built to Last: Successful Habits of Visionary Companies',
        'subtitle': 'Successful Habits of Visionary Companies',
        'authors': ['Jim Collins', 'Jerry I. Porras'],
        'category': 'Business & Economics',
        'publisher': 'HarperBusiness',
        'year': 1994,
        'pages': 368,
        'isbn': '9780060516406',
        'rating': 4.7,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Drawing on a six-year research project at Stanford Business School, Collins and Porras examine eighteen visionary companies to discover what distinguishes enduringly great institutions from their competitors.',
        'copies': 2,
        'shelf_prefix': 'Stack BIZ, Row 3, Shelf'
    },
    {
        'title': 'Rework',
        'subtitle': 'Change the Way You Work Forever',
        'authors': ['Jason Fried', 'David Heinemeier Hansson'],
        'category': 'Business & Economics',
        'publisher': 'Crown Business',
        'year': 2010,
        'pages': 288,
        'isbn': '9780307463746',
        'rating': 4.7,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'From the creators of Basecamp, Rework discards traditional corporate dogma. It shows that you need less than you think—less staff, fewer meetings, less planning—to build a wildly profitable and resilient business.',
        'copies': 3,
        'shelf_prefix': 'Stack BIZ, Row 4, Shelf'
    },

    # ── SCIENCE & MATHEMATICS ──
    {
        'title': 'The Gene: An Intimate History',
        'subtitle': 'An Intimate History',
        'authors': ['Siddhartha Mukherjee'],
        'category': 'Science & Mathematics',
        'publisher': 'Scribner',
        'year': 2016,
        'pages': 608,
        'isbn': '9781476733500',
        'rating': 4.9,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Pulitzer Prize winner Siddhartha Mukherjee traces the fascinating history of the gene from Aristotle to Mendel, Darwin, Watson and Crick, up to modern CRISPR gene-editing technologies.',
        'copies': 3,
        'shelf_prefix': 'Stack SCI, Row 1, Shelf'
    },
    {
        'title': 'The Emperor of All Maladies: A Biography of Cancer',
        'subtitle': 'A Biography of Cancer',
        'authors': ['Siddhartha Mukherjee'],
        'category': 'Science & Mathematics',
        'publisher': 'Scribner',
        'year': 2010,
        'pages': 608,
        'isbn': '9781439170915',
        'rating': 4.9,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Winner of the Pulitzer Prize. A magnificent "biography" of cancer—from its earliest recorded appearances in ancient Egyptian scrolls to the heroic twentieth-century battles to cure it.',
        'copies': 3,
        'shelf_prefix': 'Stack SCI, Row 1, Shelf'
    },
    {
        'title': 'Seven Brief Lessons on Physics',
        'subtitle': 'The International Bestseller',
        'authors': ['Carlo Rovelli'],
        'category': 'Science & Mathematics',
        'publisher': 'Riverhead Books',
        'year': 2014,
        'pages': 96,
        'isbn': '9780399184413',
        'rating': 4.7,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'A lean, poetic introduction to modern physics covering general relativity, quantum mechanics, the architecture of the cosmos, elementary particles, quantum gravity, black holes, and time.',
        'copies': 3,
        'shelf_prefix': 'Stack SCI, Row 2, Shelf'
    },
    {
        'title': 'Chaos: Making a New Science',
        'subtitle': 'The Revolutionary Science of Nonlinear Dynamics',
        'authors': ['James Gleick'],
        'category': 'Science & Mathematics',
        'publisher': 'Viking',
        'year': 1987,
        'pages': 368,
        'isbn': '9780143113454',
        'rating': 4.8,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'National Book Award Finalist. James Gleick recounts the discovery of chaos theory—from the butterfly effect to fractals and strange attractors—revealing universal order hidden in turbulent systems.',
        'copies': 2,
        'shelf_prefix': 'Stack SCI, Row 2, Shelf'
    },
    {
        'title': 'Fermat\'s Enigma: The Epic Quest to Solve the World\'s Greatest Mathematical Problem',
        'subtitle': 'The Epic Quest to Solve the World\'s Greatest Mathematical Problem',
        'authors': ['Simon Singh'],
        'category': 'Science & Mathematics',
        'publisher': 'Walker & Company',
        'year': 1997,
        'pages': 336,
        'isbn': '9780385493628',
        'rating': 4.8,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'The thrilling story of Andrew Wiles\'s seven-year secret struggle to prove Fermat\'s Last Theorem, solving a mathematical riddle that had puzzled the world\'s greatest minds for over 350 years.',
        'copies': 2,
        'shelf_prefix': 'Stack SCI, Row 3, Shelf'
    },
    {
        'title': 'The Character of Physical Law',
        'subtitle': 'The Messenger Lectures (Cornell University)',
        'authors': ['Richard Feynman'],
        'category': 'Science & Mathematics',
        'publisher': 'MIT Press',
        'year': 1965,
        'pages': 192,
        'isbn': '9780262533416',
        'rating': 4.9,
        'rights_status': 'PUBLIC_DOMAIN',
        'description': 'Nobel laureate Richard Feynman delivers seven legendary lectures on gravitation, mathematics, conservation principles, symmetry, the arrow of time, and quantum mechanics with unmatched clarity.',
        'copies': 3,
        'shelf_prefix': 'Stack SCI, Row 3, Shelf'
    },
    {
        'title': 'The Fabric of the Cosmos: Space, Time, and the Texture of Reality',
        'subtitle': 'Space, Time, and the Texture of Reality',
        'authors': ['Brian Greene'],
        'category': 'Science & Mathematics',
        'publisher': 'Knopf',
        'year': 2004,
        'pages': 592,
        'isbn': '9780375727207',
        'rating': 4.8,
        'rights_status': 'LIBRARY_LICENSED',
        'description': 'Theoretical physicist Brian Greene takes readers on an exhilarating journey through the fundamental structure of reality, from Newton\'s absolute space to Einstein\'s warped spacetime, quantum entanglement, and 11-dimensional string theory.',
        'copies': 2,
        'shelf_prefix': 'Stack SCI, Row 4, Shelf'
    }
]

def run_expansion():
    print("🚀 Commencing Library Catalog & Physical Copy Expansion Pipeline...")

    admin_user = (
        User.objects.filter(is_superuser=True).first()
        or User.objects.filter(is_staff=True).first()
        or User.objects.first()
    )

    # 1. FIND HIGHEST EXISTING ACCESSION NUMBER
    highest_acc = 1000
    for c in BookCopy.objects.all():
        m = re.search(r'LIB-(\d+)', c.accession_number)
        if m:
            highest_acc = max(highest_acc, int(m.group(1)))
    current_acc = highest_acc + 1
    print(f"📊 Starting accession numbering at: LIB-{current_acc}")

    # 2. RESOLVE AND EXPAND EXISTING 12 BOOKS MISSING PHYSICAL COPIES
    missing_copy_books = Book.objects.filter(copies__isnull=True)
    print(f"\n📦 Adding physical lending copies for {missing_copy_books.count()} existing books...")
    for book in missing_copy_books:
        book.book_type = 'BOTH'
        book.save()
        # Create 2 physical copies
        for copy_idx in range(1, 3):
            cat_code = (book.category.name[:3] if book.category else 'GEN').upper()
            shelf = f"Stack {cat_code}, Row {copy_idx}, Shelf {copy_idx * 2}"
            BookCopy.objects.create(
                book=book,
                accession_number=f"LIB-{current_acc}",
                shelf_location=shelf,
                condition='NEW',
                status='AVAILABLE'
            )
            current_acc += 1
        print(f"  ✓ Added 2 physical copies for '{book.title}' (now BOTH)")

    # 3. ADD NEW CURATED BOOKS (AS BOTH PHYSICAL AND EBOOK)
    print(f"\n📚 Ingesting {len(NEW_BOOKS_CATALOG)} brand new titles with both physical copies and digital e-books...")
    added_count = 0
    protected_root = Path(getattr(settings, 'PROTECTED_EBOOK_ROOT', settings.BASE_DIR / 'protected_ebooks'))
    os.makedirs(protected_root, exist_ok=True)

    demo_user = User.objects.filter(is_superuser=False, is_staff=False).first() or admin_user

    for b_data in NEW_BOOKS_CATALOG:
        title = b_data['title']
        isbn = b_data['isbn']
        cat_name = b_data['category']

        # Category
        cat, _ = Category.objects.get_or_create(
            name=cat_name,
            defaults={'description': f"Authoritative collection in {cat_name}.", 'is_active': True}
        )

        # Check if already exists by ISBN or title
        existing = Book.objects.filter(isbn=isbn).first() or Book.objects.filter(title__iexact=title).first()
        if existing:
            book = existing
            book.book_type = 'BOTH'
            book.save()
            print(f"  • Existing: '{title}', ensuring physical copies & e-book...")
        else:
            book = Book.objects.create(
                title=title,
                isbn=isbn,
                category=cat,
                publisher=b_data['publisher'],
                publication_year=b_data['year'],
                description=b_data['description'],
                book_type='BOTH',
                is_active=True
            )
            # Authors
            first_author = b_data['authors'][0]
            for a_name in b_data['authors']:
                author, _ = Author.objects.get_or_create(
                    full_name=a_name.strip(),
                    defaults={'bio': f"Author of '{title}' and other distinguished works."}
                )
                book.authors.add(author)

            # Cover Art
            try:
                cover_content = BookCoverGenerator.generate_cover(
                    title=title,
                    author=first_author,
                    category=cat.name,
                    isbn=isbn
                )
                book.cover_image.save(f"{isbn}.png", cover_content, save=True)
            except Exception as e:
                print(f"    Warning: cover generation error for {title}: {e}")

            added_count += 1

        # Check or Create E-Book Metadata and Reader Document
        if not hasattr(book, 'ebook_metadata') or not book.ebook_metadata:
            first_author = b_data['authors'][0]
            doc_info = {
                'title': title,
                'subtitle': b_data.get('subtitle', ''),
                'author': first_author,
                'category': cat.name,
                'publisher': b_data['publisher'],
                'publication_year': b_data['year'],
                'description': b_data['description'],
                'isbn': isbn,
                'pages': b_data['pages'],
                'average_rating': b_data['rating'],
            }
            doc_html = KaggleEBookService._generate_reader_document(doc_info)
            filename = f"{uuid.uuid4().hex}.html"
            file_path = protected_root / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(doc_html)

            EBookMetadata.objects.create(
                book=book,
                protected_filename=filename,
                original_file_name=f"{re.sub(r'[^a-zA-Z0-9_-]', '_', title)[:60]}.html",
                uploaded_by=admin_user,
                file_size=len(doc_html.encode('utf-8')),
                page_count=b_data['pages'],
                format='HTML',
                rental_price=Decimal('0.00'),
                access_mode='READ_AND_DOWNLOAD',
                rights_status=b_data['rights_status'],
                rights_text=f"{'Public Domain Classics &bull; Open Academic Access' if b_data['rights_status'] == 'PUBLIC_DOMAIN' else 'LibrarySphere Licensed Institutional Collection'}",
                max_concurrent_readers=0,
                is_active=True,
                access_note='Full interactive browser reader with text-to-speech audio support.'
            )
        elif not (protected_root / (book.ebook_metadata.protected_filename or 'dummy')).exists():
            first_author = b_data['authors'][0]
            doc_info = {
                'title': title,
                'subtitle': b_data.get('subtitle', ''),
                'author': first_author,
                'category': cat.name,
                'publisher': b_data['publisher'],
                'publication_year': b_data['year'],
                'description': b_data['description'],
                'isbn': isbn,
                'pages': b_data['pages'],
                'average_rating': b_data['rating'],
            }
            doc_html = KaggleEBookService._generate_reader_document(doc_info)
            fn = book.ebook_metadata.protected_filename or f"{uuid.uuid4().hex}.html"
            book.ebook_metadata.protected_filename = fn
            book.ebook_metadata.save(update_fields=['protected_filename'])
            with open(protected_root / fn, 'w', encoding='utf-8') as f:
                f.write(doc_html)

        # Check or Create Physical Copies
        num_copies_to_add = b_data.get('copies', 2)
        existing_copies = book.copies.count()
        needed_copies = max(0, num_copies_to_add - existing_copies)
        for i in range(1, needed_copies + 1):
            shelf = f"{b_data.get('shelf_prefix', 'Stack GEN, Row 1, Shelf')} {i + existing_copies}"
            BookCopy.objects.create(
                book=book,
                accession_number=f"LIB-{current_acc}",
                shelf_location=shelf,
                condition='NEW',
                status='AVAILABLE'
            )
            current_acc += 1

        # Patron Review
        if b_data['rating'] >= 4.5 and demo_user:
            BookReview.objects.get_or_create(
                book=book,
                user=demo_user,
                defaults={
                    'rating': 5,
                    'headline': f"Essential volume in {cat.name}",
                    'review_text': f"'{title}' is a tour de force. Exceptional depth, pristine structure, and profound clarity. An absolute must-read for our library community.",
                    'is_approved': True
                }
            )

        print(f"  ✓ Processed: '{title}' [{cat.name}] -> {book.copies.count()} physical copies & e-book ready.")

    print(f"\n========================================================")
    print(f"🎉 LIBRARY EXPANSION COMPLETE!")
    print(f"========================================================")
    print(f"  • Total Books Now in Catalog:   {Book.objects.count()}")
    print(f"  • Total Physical Copies:        {BookCopy.objects.count()}")
    print(f"  • Books Available for Borrow:   {Book.objects.filter(copies__status='AVAILABLE').distinct().count()}")
    print(f"  • Total Interactive E-Books:    {EBookMetadata.objects.filter(is_active=True).count()}")
    print(f"  • Public Domain Free Classics:  {EBookMetadata.objects.filter(rights_status='PUBLIC_DOMAIN').count()}")
    print(f"========================================================\n")

if __name__ == '__main__':
    run_expansion()
