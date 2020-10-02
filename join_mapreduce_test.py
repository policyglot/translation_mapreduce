# Adapted for MrJob from Joe Stein's example at:
# http://allthingshadoop.com/2011/12/16/simple-hadoop-streaming-tutorial-using-joins-and-keys-with-python/

import sys, os, re
import itertools
from mrjob.job import MRJob
from mrjob.step import MRStep

class MRJoin(MRJob):
  
  SORT_VALUES = True
  
  def mapper(self, _, line):    
    splits = line.rstrip("\n").split("|")
    
    if len(splits) == 2: # country data
      symbol = 'A'
      countryName = splits[0]
      country2digit = splits[1]
      yield country2digit, [symbol, countryName]
    else: # person data
      symbol = 'B'
      personName = splits[0]
      personType = splits[1]
      country2digit = splits[2]
      yield country2digit, [symbol, personName, personType]
  
  def reducer_join(self, key, values):
    #the key in the dict is the primary key of the join.
    values = [x for x in values]
    if len(values) > 1: # our join hit
      country = values[0]
      for value in values[1:]:
        yield key, [country, value]
    else: # our join missed
      pass

  def combiner(self, key, values):
    '''
    Merges the lists from the join
    '''
    #Flatten the list into one
    #flat_list = [item for sublist in values for item in sublist]
    #flatten = list(itertools.chain.from_iterable(values))
    yield key, values

  def steps(self):
    return [
        MRStep(mapper=self.mapper,
            reducer=self.reducer_join),
        MRStep(combiner=self.combiner) 
            #reducer=self.reducer_count_words)
        ]


      
if __name__ == '__main__':

  MRJoin.run()