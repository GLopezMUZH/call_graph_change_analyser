Research results
---------------------
The development of *callgraphCA* was motivated by the following research questions:

* RQ1: To what extent is it possible to build evolutionary call-graphs based on software version management information?
* RQ2: What is the relation between structural coupling (on a function level) and the call-graphs software evolution?
* RQ3: Is there a relation between conceptual (non-structural) coupling and the call-graphs software evolution?

Additional to our goal of answering the research questions, we developed *callgraphCA* as a user-friendly tool for researchers and software development teams so that they can apply its functionality to different systems. 

We present here the empirical results when applied to our systems under study, to show how *callgraphCA* can support the understanding of sofware evolution.


Change proneness
---------------------
Before the introduction of the term change coupling by Fluri et al., in 2003, Bieman et al. [107]
pointed out that frequent changes in clusters of classes might reflect functional coupling or chronic
problems in the architecture of the system; both Nagappan et al. [108] and D’Ambros et al. [40]
found that change proneness correlates stronger that coupling in the projects they studied back
then.
The summary of results analyzing the change proneness trough out the life of the systems
under study is shown in Table 5.1. For a visual aid, in Figure 5.1 we present the distribution of
number of commits per file for the projects glucosio-android and GRIP.The skewed distribution
comes from the many files changing rarely, and very few files who are often updated, this distribution
is similarly present in all of our projects. These results align with previous research,
like discussed in Section 2, that has found that many social artifacts, like social and economical
networks, present long tailed behaviours with scarce matrices. The identification of co-change
patterns in complex systems with such exponential behaviours is not a task for intuitive pattern
detection and needs support from appropriate tools.


Change coupling
---------------------
When adopting association rule learning to discover co-changing patterns, it is important to find
a balance between highly restrictive thresholds that eliminate loose couplings but reduce the number
of discovered rules to small sets that might be not actionable, and on the other side, where so
much association rules are found, with low support, the user finds them irrelevant. In Table 5.2
we display the amount of generated rules when applying the Apriori algorithm with the given
support threshold. We can observe that, the lower the threshold, the more rules will be found,
respectively more itemsets. Referring again to the study by Bavota et al. [101] on developers perception,
and taking into account the results from the table, we opted for using a support threshold
of 0.02.
In Table 5.3 we compare the logical and structural coupling at the level of file commit for the
association rules found for the projects. The first column is the number of rules found with a
threshold of 0.02. The second column displays the number of rules with itemsets that present a
structural dependency. For each project there are two rows. The first row shows rules generated
with the threshold and no limit of items, the second row shows the numbers having itemsets
larger than two. In 2018 Ajienka et al. [93] found that when two objects had a dependency, 70%
of the time they were also semantically linked. Despite our small sample and risking to leave the
project eclipse-concierge aside as an outlier, we are inclined to say that our values of the association
rules that are found to have a structural coupling seem in a range of the expected. At this point,
we need to mention the limitations and threats to validity of not slicing over time windows. For
the current implementation we compare just the existence of a structural dependency without
filtering for time periods.
With the output of the association rules, the user can easily know the number of occurrences of
each of the rule’s item’s within the set of transactions. For such purpose our analytics library offers
support functions. Figure 5.3 show_transactions_containing_items( ) displays the number of times
that items 1,2 and 1,2,3,4 existed in the transactions set, furthermore, it explains the directional
number of occurrences where the first item is the predecesor and so forward until the last item.

Call graph evolution
---------------------
