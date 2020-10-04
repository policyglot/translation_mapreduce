# translation_mapreduce
This code leverages bidirectional translation on the crowdsourced website- Tatoeba to check for accuracy of translations to English. 


**Automating Paraphrase Creation Through Parallel Corpora**

## Introduction

The phrase 'in other words' usually concludes discussions. Our discussion begins with it. ‘Paraphrases’ present alternative methods for the expression of the same meaning (Barzilay & McKeown, 2003). These variations can occur at the level of individual words, phrases or entire sentences. 

Besides domains of theoretical linguistics such as semantic similarity (Cer at al, 2017), paraphrases are assuming increased importance in the design of NLP platforms for largescale communications. For example, the United Nations’ ‘UReport’ chatbot currently provides COVID-19 information to 5 million youth in 50 countries (UNICEF, 2020). Both for interpreting diverse questions and for generating varied and human-like sentences, paraphrases become critical. (Bannard and Callison-Burch, 2005) 

However, the creation of monolingual paraphrases has proven challenging. Researchers would typically rely on manually-annotation (Wieting et al, 2019). For example, Barzilay and McKeown (2003) leveraged multiple English translations of foreign language novels. Other such resources like Word-net (Miller et al., 1990) find themselves limited to lexical (rather than phrasal or syntactic) paraphrases. 

Given this background, Bannard and Callison-Burch (2005) introduced the innovation of bilingual parallel corpora. Like with Dolan et al (2005)'s' clustering of news articles, they rely on sentence alignment as used in statistical machine translation, and identify phrases in the foreign language sentence as 'pivots' from which to discern meaning. Under such a scheme, multilingual corpora expand the realm of paraphrases from pairs to multiple possibilities. 

However, this leaves two issues unaddressed for NLP systems. Firstly, they are likely to require entire sentential (rather than phrasal) paraphrases, so as to maintain the linguistic richness that we discussed above. Secondly, the tone must remain informal to mimic human conversation. However, Wieting et al (2019) largely rely on machine translations of large corpora drawn from more formal and official sources, such as the Europarl corpus (Tiedemann, 2012).   

## Data

The Tatoeba dataset mentioned above was launched in 2006 for language learners, and thus incorporates our desired colloquial flavour of usage. In this exploration, we begin with the section of the project that was provided sentence-alignment through OPUS (Tiedemann, 2012), which expands the corpus size to 7.8 million sentences in 338 languages. In this exploration, we will be downloading two tables on [Tatoeba's public interface].(https://tatoeba.org/eng/downloads) Unlike Scherrer (2020)’s exploration of the same dataset through multilingual graph structures, we will rely on a MapReduce framework. 

*Links Table*
Provides the IDs of sentences that are considered to be translations. The relationship is always symmetric. If Sentence A is a translation of Sentence B, then vice-versa is true too. 
This table does not contain any details whatsoever about the sentences that are referenced by the IDs. In total, it contains 17,284,698 entries. In our code, we assign it the symbol of 'L'.

*Sentences Table*
It provides the ID for each sentence, along with its core text and language code. In the interests of simplicity, we downloaded only the English sentences, which consist of 1,323,161 rows (or roughly 12% of the full data). 

## Method
While PySpark and its SQL module may have provided a viable option, we would most likely have had to execute complicated self-referencing nested queries. Some initial explorations of this direct merging-based approach are available in the 'tatoeba-combine' Jupyter notebook. Given these concerns, MapReduce approaches emerge as the most suitable method. The link from an original sentence to a translation fits with the key-value paradigm. Unlike the concept of keys in databases, the stages of a map-reduce ‘job’ do provide the leverage to merge the values of data with matching keys. 
For ease of understanding, this section will rely two sample datasets- ‘links_test.csv’ and ‘sentences_test.csv’- available in this repo. 


###Stage 1*: 
The Mapper: The mapper takes both source tables and splits them into rows, which are scattered across clusters. Each row is split on the tab separator, and each index of the resulting row is assigned a variable name that matches with the corresponding field in the original table. 
So for example, our toy dataset produces the following results:
- "1"     ["S", "i like to eat meat"]
- "2"     ["S", "i'm non-vegetarian"]
- "3"     ["S", "i like goats."]
- "4"     ["S", "me gusta comer la carne."]
- "5"     ["S", "me gusta penelope cruz."]
- "6"     ["S", "soy carnivoro"]
- "1"     ["L", "4"]
- "2"     ["L", "4"]
- "4"     ["L", "1"]
- "4"     ["L", "2"]
- "6"     ["L", "1"]
- "6"     ["L", "2"]

Since mappers do not inherently understand whether the row originated from the Sentence or Links Table, we indicate this explicitly through the 'L' and 'S' symbols, as well as the number of columns resulting from the split (2 and 3 for Links and Sentences) respectively. 
The Reducer:
The rows are now merged based on the shared key on the left. Unmatched rows are eliminated. 

- "1"     ["S", "i like to eat meat", "L", "4"]
- "2"     ["S", "i'm non-vegetarian", "L", "4"]

Here, we see a considerable reduction in the input size. Though sentence 4 and 6 in Spanish may have been paraphrases, our code excluded all non-English pairs for the present iteration of this project. 

### Stage 2*

The Combiner: The matching key for the pair of translations is brought out from the values. The original sentence IDs are abandoned. 

- "4"     "i like to eat meat"
- "4"     "i'm non-vegetarian"

The Reducer: After matching the paraphrases into one list, we dispense with the ID of the original. This leaves us with just the paraphrase set as the final output. 

- "i like to eat meat"    "i'm non-vegetarian"

In this way, we may arrive at a set of paraphrases that can be cross-checked with the TaPaCo dataset as generated in Scherrer(2020)'s analysis.

## Future Extensions*

This project could be extended to other non-Roman script languages using Unicode tweaks, as well as other crowdsourced bilingual datasets such as OpenSubtitles, whose XML-based dataset has yet to be parallelized.  In other words, 'in other words' can combine the latest advances in computational linguistics and social science research to build rich and varied communications that scale. 
