# Elisio

## Introduction

The Elisio project is an attempt to teach computers to scan Latin verses, and to share the results publicly with those who are interested.
Scanning a Latin verse means, in this technical context, to analyze its structural variation of light and heavy syllables.
While this is an ancient art, practiced by the Romans themselves and almost ever since, this kind of data is hard to digitalize manually.

With this scanning engine, we want to allow users to do scans of Latin verses,
in hopes that they can eventually retrieve previously unknown information from this heavily stylized use of the Latin language.

## Approach

In scanning a verse, this is a very high-level description of the approach that we took:

1. split the verse into words
2. analyze the letters: remove reading marks, resolve writing conventions (v => u)
3. combine letters into sounds (qu is one sound, *muta cum liquida* also for our purposes)
4. combine sounds into syllables, taking into account the possible ambiguity of semivowels
5. try to determine syllable weights based on the basic weight rules
6. try to see, from the syllable count, whether the verse can legally be a hexameter, pentameter, ... verse
7. try to determine the full verse from the known weights

## Problems and limitations

A small but persistent minority of verses in the extant corpus will probably never be scannable by this algorithm without human intervention.
The problematic types of verses include:

* verses with rare (usually Greek) names, especially if they defy the normal weight rules
* verses with words that must be scanned in non-intuitive ways (e.g. Verg. Aen. I, 2: La-vin-ia is trisyllabic)
* half-verses, most commonly in Vergilius
* verses that have a hiatus
* verses with verb forms that may derive from either volvo or volui (perfect tenses of velle)

Less severe problems include:
* rare words in verses where information is already scarce
* hypermetric verses, again most commonly in Vergilius
* words that have lots of possible declensions (adjectives and verbs), which makes exact word hits less likely

The unique-word problem can be mitigated, hopefully, by teaching Elisio to recognize declensions and conjugations.
This work is ongoing.

The verse analysis algorithm is currently only implemented for hexameters, pentameters, and some common lyrical meters.
The scanning horror of the dramatic meters is not on the realistic roadmap for now.

## Technology

The Elisio engine is built using the programming language Python. It uses the project Whitaker's Words, which I am modifying
heavily to suit the needs of this project.

## License

Elisio is released under the Affero General Public License (AGPL), a strong copyleft license which still gives third parties
considerable freedom to use the source code contained in this project.
If you are considering forking Elisio or using some of its algorithms,
please check [the license terms](./LICENSE.md) to make yourself acquainted with your rights and obligations.

**Ignorance is not a valid excuse.**

As mentioned in the header of `numerals.py`, that file is still available under its original PSF license.

## Code of Conduct

This project includes a [code of conduct](./CODE_OF_CONDUCT.md) and tries to adhere to it strictly.

## Further developments

If you're feeling Pythonic, you can look at [the CONTRIBUTING file](./CONTRIBUTING.md) for the contributor guide,
and read [the TODO file](./TODO.md) to see the high-level features we'd like to work on next.

## Major contributors

This project was started by Benoit Lagae as a hobby assignment, coming from his background in Latin linguistics
and his Master's thesis research.
