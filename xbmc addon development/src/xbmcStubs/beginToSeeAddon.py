#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 29/04/2014

@author: Alex Montes Barrios
'''
index = [
         ['MN-2', 'All the Taints', 'The Buddha teaches the bhikkhus seven methods to restrain and eventually destroy all the taints (&#257;savas).', 8],
         ['MN-4', 'Fear and Dread', 'The Buddha explains to a brahmin what is needed to practice alone in the jungle without fear and dread, beginning with overcoming the five hindrances. He then goes on to describe his own experience of conquering fear when striving for enlightenment. He entered into the four jh&#257;nas and on three watches of the night attained the three knowledges: the recollection of his past lives, the passing away and reappearance of beings (according to their actions), and the Four Noble Truths.', 4],
         ['MN-5', 'Without Blemishes', 'Ven. S&#257;riputta gives a discourse on the meaning of blemishes, explaining that a bhikkhu becomes blemished when he falls under the sway of evil wishes. He describes the advantages of abandoning these evil wishes, thereby gaining honor, respect, reverence, and veneration.', 0],
         ['MN-9', 'Right View', 'This comprehensive discourse is given by Ven. S&#257;riputta. He begins by defining what is wholesome and the root of the wholesome, and what is unwholesome and the root of the unwholesome. Using the format of the Four Noble Truths (understanding the object, the origin of the object, the cessation of the object, and the way leading to the cessation of the object), he goes through nutriment, the Four Noble Truths, and all twelve factors of dependent origination.', 6],
         ['MN-10', 'The Foundations of Mindfulness', 'This is the most important discourse by the Buddha on the training of mindfulness meditation, with particular attention given to developing insight. The Buddha begins by declaring that the four foundations of mindfulness are the direct path leading to the realization of Nibb&#257;na. He then gives detailed instructions on the four foundations: the contemplation of the body, feelings, mind, and mind objects.', 28],
         ['MN-12', 'The Greater Discourse on the Lion&rsquo;s Roar', 'In this discourse, the Buddha talks about his many superior qualities, including a list of ten powers of the Tath&#257;gata and many other lists that show explicitly how spiritually advanced he is. Of particular interest is his description of the time he practiced austerities.', 3],
         ['MN-13', 'The Greater Discourse on the Mass of Suffering', 'The Buddha explains what is the gratification and danger of, and escape from, sensual pleasures. He explains the danger of sense pleasures, ascribing the cause of the mass of suffering as clinging to sense pleasures. He also explains the gratification and danger of, and escape from, material form and feeling.', 1],
         ['MN-18', 'The Honeyball', 'This is an important discourse on papa&ntilde;ca. Papa&ntilde;ca is the proliferation and projection of mind that emerges from the process of cognition, and gives rise to perceptions and notions that overwhelm and victimize a person. After the Buddha has finished speaking, Ven. Mah&#257; Kacc&#257;na gives the detailed meaning.', 2],
         ['MN-19', 'Two Kinds of Thought', 'The Buddha divides thought into two classes: thoughts of sensual desire, ill will and cruelty&#894; and thoughts of renunciation, non-ill will (mett&#257;) and noncruelty (karu&#7751;&#257;). This discourse states simply that unwholesome thought bring about unhappiness, and wholesome thoughts bring about happiness. Unwholesome thoughts can be replaced by wholesome thoughts (and, even better, a quiet, collected mind). Knowing this, we can bring about happiness and freedom from pain.', 9],
         ['MN-20', 'The Removal of Distracting Thoughts', 'Five methods of removing distracting thoughts are presented, but the last four may have been added by Brahmins some time after the time of the Buddha.', 17],
         ['MN-21', 'The Simile of the Saw', 'This discourse is a challenging and relevant training on how to develop compassion, lovingkindness, equanimity and patience even when we are physically attacked or fatally wounded by someone.', 7],
         ['MN-26', 'The Noble Search', 'The Buddha gives the bhikkhus a long account of his own quest for enlightenment from the time of his life in the palace through to his transmission of the Dharma to his first five disciples.', 1],
         ['MN-27', "The Shorter Discourse on the Simile of the Elephant's Footprint", 'The Buddha uses the simile of the elephant&rsquo;s footprint to show how one must not come to a conclusion too hastily about the certainty of whether one is fully enlightened. This applies to whether the Dharma is well proclaimed by the Buddha and whether the Sangha is practicing the good way.', 5],
         ['MN-28', 'The Greater Discourse on the Simile of the Elephant&rsquo;s Footprint -', 'Mah&#257;hatthipadopama Sutta', 1],
         ['MN-29', 'The Greater Discourse on the Simile of the Heartwood', 'The Buddha uses the simile of a great tree possessed of heartwood, sapwood, inner bark and outer bark, twigs and leaves, to point out how the holy life is not for gain, honor and renown; virtue; the attainment of concentration; nor for knowledge and vision. It is for the unshakable deliverance of the mind.', 1],
         ['MN-30', 'The Shorter Discourse on the Simile of the Hartwood', 'Using the simile of a great tree possessed of heartwood, sapwood, inner bark and outer bark, twigs and leaves, the Buddha points out how the holy life is not for gain, honor and renown, nor simply for the attainment of virtue, nor the attainment of collectedness, nor for knowledge and vision. It is for the unshakable deliverance of the mind. This is the goal of this holy life, its heartwood, and its end.', 3],
         ['MN-35', 'TheShorterDiscoursetoSaccaka- C&#363;&#7735;asaccakaSutta', 'Thisisagood storywhereSaccaka,aNiga&#7751;&#7789;ha&rsquo;sson who considered himself an unexcelled debater, tries to take on the Buddha, who then turns Saccaka&rsquo;s assertions upside&shy;down. He demonstrates to Saccaka that the five aggregates are not&shy;self because one can gain no mastery over them.', 1],
         ['MN-36', 'The Greater Discourse to Saccaka', 'This is another dialogue with Saccaka. This time the Buddha describes what it means when an arisen pleasant feeling does not invade one&rsquo;s mind and remain because the body is developed, and arisen painful feeling does not invade one&rsquo;s mind and remain because the mind is developed. He gives another account of his experiences before his enlightenment (compare with MN 26).', 3],
         ['MN-37', 'The Shorter Discourse on the Destruction of Craving', 'Wishing to discover if Sakka, ruler of gods, has understood the meaning of a short discourse the Buddha had given to him, Ven. Mah&#257; Moggall&#257;na makes a brief trip to the Heaven of the Thirtythree. The Buddha had told Sakka that nothing is worth clinging to, and that, whatever feelings arise, one should contemplate the impermanence in those feelings.', 1],
         ['MN-38', 'The Greater Discourse on the Destruction of Craving', 'This is an important discourse on dependent origination and the destruction of craving. After reprimanding the bhikkhu S&#257;ti about the view he was proclaiming&mdash;that the same consciousness runs through the round of rebirths&mdash; the Buddha explains from every angle the correct way to view dependent origination, showing how all phenomena of existence arise and cease through conditions.', 26],
         ['MN-39', 'The Greater Discourse at Assapura', 'This is another  \t\t\t\t\t\t\t\t\t\t\t\t\t\tdiscourse where the  \t\t\t\t\t\t\t\t\t\t\t\t\t\tBuddha lists what a  \t\t\t\t\t\t\t\t\t\t\t\t\t\tbhikkhu should do to  \t\t\t\t\t\t\t\t\t\t\t\t\t\tundertake the training  \t\t\t\t\t\t\t\t\t\t\t\t\t\tas a recluse (as in MN53  \t\t\t\t\t\t\t\t\t\t\t\t\t\tand MN107).', 2],
         ['MN-43', 'The Greater Series of Questions and Answers', 'Ven. Mah&#257; Ko&#7789;&#7789;hita meets with Ven. S&#257;riputta and asks questions about the Dharma in order to refine his understanding. This discourse expounds various subtle points of Dhamma.', 14],
         ['MN-44', 'The Shorter Series of Questions and Answers', 'This discourse is a discussion between bhikkhuni Dhammadinn&#257; and her former husband, the lay follower Vis&#257;kha. It includes many excellent points on identity, feelings (vedan&#257;), cessation and Nibb&#257;na.', 12],
         ['MN-46', 'The Greater Discourse on Ways of Undertaking Things - Mah&#257;dhammasam&#257;d&#257;na Sutta', 'Here the Buddha clearly and simply states the truth of cause and effect. He shows how we can bring about our own transformation by applying wisdom to the way we undertake things. An ignorant person does not know what things should and should not be cultivated and followed. A wise person knows what things should and should not be cultivated and followed. Examples are given for each.', 3],
         ['MN-47', 'The Inquirer -V&#299;ma&#7747;saka Sutta', 'The Buddha invites the bhikkhus to make an investigation of himself (the Buddha) in order to find out whether or not he is fully enlightened. He gives them a list of criteria to review.', 1],
         ['MN-48', 'The Kosambians', 'When the bhikkhus at Kosamb&#299; are engaged in a dispute, the Buddha teaches them six qualities that create love and unity. Of the last and &ldquo;highest&rdquo; quality, right view, he teaches seven more qualities that will, if practiced, lead one to the complete destruction of suffering. These are also called the seven knowledges attained by a stream enterer.', 4],
         ['MN-52', 'The Man from A', '&#7789;&#7789;', 2],
         ['MN-53', 'The Disciple in Higher Training', 'Ven. &#256;nanda gives a discourse at the Buddha&rsquo;s request on the fifteen factors involved in higher training for a disciple who has entered upon the way.', 10],
         ['MN-55', 'To Jivaka', 'This is the discourse in which the Buddha lays down his rules for eating meat. He clearly states that what makes food permissible and blameless has to do with the attitude with which the food is eaten, rather than the food itself, in this case, meat.', 1],
         ['MN-59', 'The Many Kinds of Feeling', 'The Buddha clears up the question of why someone may be confused as to how many kinds of feeling there are, for he has presented many different lists. This discourse also describes the progressive pleasure one attains from the eight meditative attainments, and from the attainment of cessation.', 13],
         ['MN-62', 'The Greater Discourse of Advice to R&#257;hula', 'The Buddha advises Ven. R&#257;hula to practice a variety of meditations: on the emptiness of the five aggregates, on the five elements, on the four brahmavih&#257;ras, on foulness, on impermanence, and on mindfulness of breathing.', 1],
         ['MN-63', 'The Shorter Discourse to M&#257;luunky&#257;putta', 'The monk who was given this discourse by the Buddha was prepared to leave the holy life if the Buddha could not declare what he had left undeclared. The Buddha makes quite clear what he has and has not declared and why. The monk was satisfied.', 0],
         ['MN-66', 'The Simile of the Quail', 'The Buddha gives a teaching to Ven. Ud&#257;yin on the importance of abandoning every fetter, no matter how trivial it may seem, including any attachment to the eight meditative attainments. Included are some good similes on how the situation itself is not what determines whether something is binding or not, but how one views it.', 3],
         ['MN-70', 'At K&#299;&#7789;&#257;giri', 'While admonishing two monks, the Buddha asks them if they have ever known him to give teachings that did not make wholesome states increase, and unwholesome state decrease. He also tells them of the seven kinds of noble persons in the world.', 2],
         ['MN-71', 'To Vacchagotta on the Threefold True Knowledge -Tevijjavacchagotta Sutta', 'In this short conversation between the Buddha and Vacchagotta, the Buddha denies possessing complete knowledge of everything at all times and in all states. He says the correct description of him would be that he possesses the Threefold Knowledge: recollection of his past lives, ability to see the lives of others, and true deliverance of mind by wisdom.', 1],
         ['MN-75', 'To', 'M&#257;gandiya', 1],
         ['MN-77', 'The Greater Discourse to Sakulud&#257;yin', 'This is a long discourse given to a group of well known wanderers. It reviews the Buddha&rsquo;s whole progression of teachings, providing information that is repeated throughout the discourses. The Buddha gives five reasons for why he is venerated and honored.', 5],
         ['MN-89', 'Monuments to the Dharma-Dhammacetiya Sutta', 'King Pasenadi offers ten reasons why he shows such deep veneration to the Buddha, Dharma and Sangha.', 1],
         ['MN-91', 'Brahm&#257;yu -', 'Brahm&#257;yu Sutta', 1],
         ['MN-95', 'With Canki', 'The Buddha shows the difference between preserving the truth (out of faith), discovering the truth (out of direct experience through practice), and the arrival at truth.', 10],
         ['MN-98', 'To V&#257;se&#7789;&#7789;ha', 'The Buddha resolves a dispute between two young brahmins about whether a', 0],
         ['MN-105', 'To Sunakkhatta', "The Buddha discusses with Sunakkhatta the problem of someone overestimating his or her level of attainment. He is basically saying that if one really knows the cause of bondage (which is craving), then one would not do things that arouse one's mind toward any object of attachment. There are those who say they are intent only on Nibb&#257;na but their actions are not congruent with their statement. This is a very good basic prescription from the Surgeon (the Buddha), which is essentially the heart of the teaching on how to heal the wound of suffering.", 4],
         ['MN-106', 'The Way to the Imperturbable', 'The Buddha explains the approaches to various levels of higher meditative states culminating in Nibb&#257;na. He points out how one can get caught in clinging at any of these levels. The imperturbable refers to the 4th jh&#257;na and the 1st two immaterial states.', 10],
         ['MN-107', 'To Ga&#7751;aka Moggall&#257;na', 'Ga&#7751;aka Moggall&#257;naasks the Buddha to describe the gradual training in this Dharma and Discipline. Then the Buddha gives a good simile on why some disciples reach the goal and some do not.', 8],
         ['MN-109', 'The Greater Discourse on the Fullmoon Night', 'In a large gathering of disciples, one who is a teacher of many students asks the Buddha questions in the hope that it will help to refine his students&rsquo; understanding of not-self, primarily by exploring the emptiness of the five aggregates.', 1],
         ['MN-111', 'One by One as They Occurred', 'The Buddha describes Ven. S&#257;riputta&rsquo;s attainment to arahatship as it occurred through the jh&#257;nas.', 24],
         ['MN-112', 'The Sixfold Purity', 'If someone claims to have attained final knowledge, the Buddha expounds on how that person should be questioned, and on what the nature of his or her answer should be. The discourse includes an indepth description of the Buddha&rsquo;s liberated mind, thereby showing every possible way that clinging can arise and be extinguished.', 5],
         ['MN-113', 'The True Man', 'The Buddha distinguishes the character of an &ldquo;untrue man&rdquo; and a &ldquo;true man.&rdquo;', 9],
         ['MN-114', 'To Be Cultivated and Not To Be Cultivated', 'Ven. S&#257;riputta fills in the details of the Buddha&rsquo;s outline on what should be cultivated and what should not. This discourse is quite specific and is a supplement to MN-9 and MN-41.', 1],
         ['MN-115', 'The Many Kinds of Elements', 'The Buddha expounds in detail the elements, the six sense bases, dependent origination, and the kinds of situations that are possible and impossible in the world (for one who has right view.)', 1],
         ['MN-117', 'The Great Forty', 'The Buddha defines the factors of the Noble Eightfold Path and explains their interrelationships. One interesting aspect of this discourse is that it clearly shows the Noble Eightfold Path as a way to practice not only for ordinary persons, but also for those who have already entered the stream.', 5],
         ['MN-118', 'Mindfulness of Breathing', 'A very important discourse explaining mindfulness of breathing and how it relates to the four foundations of mindfulness, to the seven enlightenment factors, and to true knowledge and deliverance.', 1],
         ['MN-119', 'Mindfulness of the Body', 'The Buddha explains how mindfulness of the body is developed and cultivated so that one can receive great benefits. The jh&#257;nas are also included as a way of developing mindfulness of the body.', 1],
         ['MN-121', 'The Shorter Discourse on Voidness', 'Sutta', 7],
         ['MN-122', 'The Greater Discourse on Voidness', 'Seeing that the bhikkhus were growing fond of socializing, the Buddha stresses the importance of seclusion: to enter and abide in voidness internally and externally if one wants to obtain, without difficulty, the bliss of enlightenment.', 3],
         ['MN-128', 'Imperfections', 'This discourse has two parts. In the first, there is more information about living in concord, arising from the dispute at Kosamb&#299; (as in MN-48). It includes a famous series of stanzas about living with non-hatred. In the second, the Buddha discusses the various impediments to meditative progress.', 10],
         ['MN-133', 'Mah&#257;kacc&#257;nabhaddekaratta Sutta', 'A summary and exposition on a verse about how one revives the past, puts hope in the future and gets embroiled in the present, and how not to do this. The Buddha emphasizes the need for present effort in seeing things as they are. The Buddha gives the teaching in brief. After he leaves for his dwelling, Mah&#257; Kacc&#257;na analyzes the verse by way of the twelve sense bases.', 1],
         ['MN-135', 'The Shorter Exposition of Action', 'The Buddha explains how karma accounts for one&rsquo;s fortune or misfortune. He names the results of specific actions.', 6],
         ['MN-136', 'The Greater Exposition of Action', 'The Buddha reveals subtler complexities on the workings of kamma that overturn simplistic dogmas and sweeping generalizations.', 1],
         ['MN-138', 'The Exposition of a Summary', 'In this discourse, Ven. Mah&#257; Kacc&#257;na answers questions about what it means for consciousness to be scattered and distracted externally, what it means for the mind to be stuck, what it means for consciousness to be agitated due to clinging, and how to end these difficulties. This is a useful discourse.', 1],
         ['MN-140', 'The Exposition of the Elements - Dh&#257;tuvibhanga Sutta', 'This is a profound and touching account of the Buddha&rsquo;s meeting with Pukkus&#257;ti (a former king), who had gone forth but had never met the Buddha. The Buddha could tell he was ripe for awakening, so he gave him a private teaching without Pukkus&#257;ti&rsquo;s knowing he was the Buddha. Primarily, the discourse is about four foundations: wisdom, truth, relinquishment and peace. It also includes a great deal on feeling (vedan&#257;). The last section is about mental conceiving. When Pukkus&#257;ti went out to look for a proper robe and bowl for his ordination, he was killed by a cow and reborn in the Avih&#257; heaven as a nonreturner.', 3],
         ['MN-141', 'The Exposition of the Truths - Saccavibhanga Sutta', 'Ven. S&#257;riputta gives a fairly detailed summary of the Four Noble Truths. There is a more detailed analysis in the Mah&#257;satipa&#7789;&#7789;h&#257;na Sutta in the D&#299;gha Nik&#257;ya (DN 22.18).', 2],
         ['MN-143', 'Advice to An&#257;thapi&#7751;&#7693;ika - An&#257;thapi&#7751;&#7693;ikov&#257;da Sutta', 'The householder An&#257;thapi&#7751;&#7693;ika is on his deathbed and calls for Ven. S&#257;riputta, in whom he has full confidence. The venerable gives him a sermon on nonclinging in order to release him from his pain.', 1],
         ['MN-145', 'Advice to Pu&#7751;&#7751;&#257; -', 'Pu&#7751;&#7751;ov&#257;da Sutta', 1],
         ['MN-146', 'Advice from Nandaka', 'Ven. Nandaka gives the bhikkhunis a discourse on impermanence. This is a standard discourse on this topic, with emphasis on the impermanence of feelings.', 2],
         ['MN-148', 'The Six Sets of Six', 'A profound and penetrating discourse on the contemplation of all the factors ofsense experience as not self.', 16],
         ['MN-149', 'The Great Sixfold Base', 'This brief discourse is a complete, clear, and direct discourse explaining the cause of suffering and its end. If one has wrong view about the six sense bases (not seeing things as they actually are with wisdom, which implies not seeing the three characteristics), then this leads to more suffering and the continuation of being. If one has right view, this leads to liberation.', 1],
         ['MN-152', 'The Development of the Faculties', 'This is a useful discourse on the supreme development of the five sense faculties. Essentially, the Buddha describes how to control the mind&rsquo;s reactivity to agreeable, disagreeable and indifferent formations so that one can be established in equanimity. The discourse contains many very good similes.', 5]]

dhammaTalks = [
               ['/mn-002-ws-110120.html', '20-Jan-11', 'Winter Series', False, True, '00:51:46', 'dr50Y1kCEjc'],
               ['/mn-002-sand-120326.html', '26-Mar-12', 'San Diego', False, True, '01:23:12', 'iSwDrWENbQI'],
               ['/mn-002-k1-kor-121106.html', '6-Nov-12', 'Korea 1 kor', False, True, '01:33:56', '2oXh3CW9MO8'],
               ['/mn-002-kay1-ind-121220.html', '20-Dec-12', 'K&#257;yagat&#257;sati 1 ind', False, True, '01:19:09', '_rNOoR8iM1E'],
               ['/mn-002-jt8-130316.html', '16-Mar-13', 'Joshua Tree 8', False, True, '00:27:51', 'CtKS4sQULFc'],
               ['/mn-009-jul07.html', 'July 07', 'DSMC', False, True, '01:05:32', 'IYnXabugl9c'],
               ['/mn-009-043-jt3-080312.html', '12-Mar-08', 'Joshua Tree 3', False, True, '01:38:55', 'je_57lGVtcY'],
               ['/mn-009-ws-110125.html', '25-Jan-11', 'Winter Series', False, True, '01:03:11', 'IrK9gYNQJ6I'],
               ['/mn-009-dsmc-130723.html', '23-Jul-13', 'DSMC', False, True, '01:14:12', 'Ca7LR_h31zs'],
               ['/mn-010-p1-jt3-080305.html', '5-Mar-08', 'P1   Joshua Tree 3', False, True, '01:32:51', '13sNUjL5nko'],
               ['/mn-010-p2-jt3-080306.html', '6-Mar-08', 'P2   Joshua Tree 3', False, True, '02:15:37', 'dXB8L2inZAI'],
               ['/mn-010-p2-jt4-090304.html', '4-Mar-09', 'P2   Joshua Tree 4', False, True, '01:39:48', '4i_vzQCIygE'],
               ['/mn-010-ana1-091205.html', '5-Dec-09', 'Anaheim 1', False, True, '02:03:20', 'gUTJAn1XPXk'],
               ['/mn-010-bog1-ind-101210.html', '10-Dec-10', 'Bogor 1 ind', False, True, '02:15:25', 'r1sNILuHAx4'],
               ['/mn-010-ws-110127.html', '27-Jan-11', 'Winter Series', False, True, '01:01:25', '2zIOTYNdX4g'],
               ['/mn-010-p1-k2-kor-121121.html', '21-Nov-12', 'P1   Korea 2 kor', False, True, '01:31:34'],
               ['/mn-010-p2-k2-kor-121122.html', '22-Nov-12', 'P2   Korea 2 kor', False, True, '01:28:04', 'Pq86qx8hkMc'],
               ['/mn-010-p1-kay1-ind-121222.html', '22-Dec-12', 'P1   K&#257;yagat&#257;sati 1 ind', False, True, '01:43:42', 'uSAWmUdrrtw'],
               ['/mn-010-p2-kay1-ind-121223.html', '23-Dec-12', 'P2   K&#257;yagat&#257;sati 1 ind', False, True, '02:08:02', '2ic0Fbj_LKw'],
               ['/mn-010-boj1-ind-130106.html', '6-Jan-13', 'Bojanga 1 ind', False, True, '01:57:35', '6M4R9eq69yc'],
               ['/mn-010-jt8-130318.html', '18-Mar-13', 'Joshua Tree 8', False, True, ' 2:00:12', 'xVj6H9nAo5U'],
               ['/mn-010-p1-dsmc-130527.html', '27-May-13', 'P1  DSMC', False, True, '1:39:33 ', 'wvKXaY2Dt3c'],
               ['/mn-010-p2-dsmc-130528.html', '28-May-13', 'P2  DSMC', False, True, '01:50:42', '_B_-2CQLGAI'],
               ['/mn-018-jt6-110315.html', '15-Mar-11', 'Joshua Tree 6', False, True, '01:21:13', 'noNqbuMS1ww'],
               ['/mn-019-sea1-070330.html', '30-Mar-07', 'Seattle 1', False, True, '01:04:49', 'e8s-WSXQjNk'],
               ['/mn-019-ws-110210.html', '10-Feb-11', 'Winter Series', False, True, '01:18:06', 'qMeouzszlus'],
               ['/mn-019-jt6-110307.html', '7-Mar-11', 'Joshua Tree 6', False, True, '02:04:17', 'HM-wgVDM838'],
               ['/mn-019-dsmc-130707.html', '7-Jul-13', 'DSMC', False, True, '00:57:44', '7lUefVv2p6s'],
               ['/mn-020-sea1-070324.html', '24-Mar-07', 'Seattle 1', False, True, '01:04:49', 'HjTq_of2qsA'],
               ['/mn-020-cym1-071122.html', '22-Nov-07', 'Chuang Yen M.', False, True, '01:47:56', 'SwuKKBpVCyo'],
               ['/mn-020-jt4-090301.html', '1-Mar-09', 'Joshua Tree 4', True, True, '01:14:54', 'LLFs2oN3ugQ'],
               ['/mn-020-bog1-ind-101208.html', '8-Dec-10', 'Bogor 1 ind', False, True, '02:07:22', '00AzuarYb-I'],
               ['/mn-020-jt6-110306.html', '6-Mar-11', 'Joshua Tree 6', False, True, '01:22:30', 'GfWP3NWnkh0'],
               ['/mn-020-k1-kor-121104.html', '4-Nov-12', 'Korea 1 kor', False, True, '01:24:59', 'rLXrg4_RSE8'],
               ['/mn-020-k2-kor-121119.html', '19-Nov-12', 'Korea 2 kor', False, True, '01:28:21', 'aXEb_Qm9G7o'],
               ['/mn-020-boj1-ind-130104.html', '4-Jan-13', 'Bojanga 1 ind', False, True, '01:56:42', 'KoGy87J3NR4'],
               ['/mn-021-8fp-jt5-100312.html', '12-Mar-10', 'Joshua Tree 5', True, True, '01:40:54', 'zVCf_yo3BfY'],
               ['/mn-021-152-jt5-100319.html', '19-Mar-10', 'Joshua Tree 5', True, True, '00:40:45', 'SLJ7YKSY_b0'],
               ['/mn-021-k1-kor-121111.html', '11-Nov-12', 'Korea 1 kor', False, True, '01:38:36', 'eRqgO0dBvOE'],
               ['/mn-021-k2-kor-121126.html', '26-Nov-12', 'Korea 2 kor', False, True, '01:59:02', 'ITBzHkSiyWE'],
               ['/mn-021-kay1-ind-121228.html', '28-Dec-12', 'K&#257;yagat&#257;sati 1 ind', False, True, '00:41:15', 'Vy2Q1u1nuNI'],
               ['/mn-021-boj1-ind-130111.html', '11-Jan-13', 'Bojanga 1 ind', False, True, '01:15:01', 'TlXx1DDpDvQ'],
               ['/mn-021-jt8-130323.html', '23-Mar-13', 'Joshua Tree 8', False, True, '00:52:01', '2uPWuhcdxHE'],
               ['/mn-029-030-080725.html', '25-Jul-08', 'DSMC', True, True, '01:11:50', '7lUefVv2p6s'],
               ['/mn-030-sea1-070328.html', '28-Mar-07', 'Seattle 1', False, True, '01:26:34', 'He4Ge9-SF1U'],
               ['/mn-029-030-080725.html', '25-Jul-08', 'DSMC', True, True, '01:11:50', '7lUefVv2p6s'],
               ['/mn-035-dsmc-130805.html', '5-Aug-13', 'DSMC', False, True, '01:16:45', 'YooFN1GVJf0'],
               ['/mn-038-jt3-080309.html', '9-Mar-08', 'Joshua Tree 3', False, True, '01:36:46', 'N-CjshxkWIc'],
               ['/mn-038-jt4-090305.html', '5-Mar-09', 'Joshua Tree 4', False, True, '02:04:46', 'OVk7fq9Drtg'],
               ['/mn-038-jt5-100310.html', '10-Mar-10', 'Joshua Tree 5', False, True, '01:52:30'],
               ['/mn-038-bog1-ind-101211.html', '11-Dec-10', 'Bogor 1 ind', False, True, '02:36:00', '4mN6KEQnme0'],
               ['/mn-038-ws-110123.html', '23-Jan-11', 'Winter Series', False, True, '02:07:33', 'j2KaTzXpQ50'],
               ['/mn-038-jt6-110309.html', '9-Mar-11', 'Joshua Tree 6', False, True, '01:50:35', 'eckL93HIeqk'],
               ['/mn-038-jt7-120319.html', '19-Mar-12', 'Joshua Tree 7', False, True, '02:13:24', 'XxIq3slKmQ0'],
               ['/mn-038-k1-kor-121107.html', '7-Nov-12', 'Korea 1 kor', False, True, '02:23:02', 'gKYoHJXj9to'],
               ['/mn-038-kay1-ind-121224.html', '24-Dec-12', 'K&#257;yagat&#257;sati 1 ind', False, True, '02:08:00', 'tN4CfB01FU4'],
               ['/mn-038-boj1-ind-130107.html', '7-Jan-13', 'Bojanga 1 ind', False, True, '02:32:51', 'pdt1jecbWXg'],
               ['/mn-038-jt8-130319.html', '19-Mar-13', 'Joshua Tree 8', False, True, '01:28:22', 'IfI7IdztldQ'],
               ['/mn-009-043-jt3-080312.html', '12-Mar-08', 'Joshua Tree 3                 Video      01:38:5', True, True, '01:38:55', 'je_57lGVtcY'],
               ['/mn-043-dsmc-080724.html', '24-Jul-08', 'DSMC', False, True, '01:09:25', 'vTW6SnL-MDM'],
               ['/mn-043-bog1-ind-101213.html', '13-Dec-10', 'Bogor 1 ind', False, True, '02:29:31', 'KmbED19Hvw8'],
               ['/mn-043-ws-110124.html', '24-Jan-11', 'Winter Series', False, True, '00:58:41', 'Ezt9mABXi2A'],
               ['/mn-043-jt6-110314.html', '14-Mar-11', 'Joshua Tree 6', False, True, '01:34:49', 'c-p7NLN_lc8'],
               ['/mn-043-jt7-120322.html', '22-Mar-12', 'Joshua Tree 7', False, True, '01:35:02', 'VPAS1vVh560'],
               ['/mn-043-dsmc-120719.html', '19-Jul-12', 'DSMC', False, True, '01:17:27', 'BE5h1LputXA'],
               ['/mn-043-k1-kor-121109.html', '9-Nov-12', 'Korea 1 kor', False, True, '02:02:35', 'Dz03V6qQsG8'],
               ['/mn-043-boj1-ind-130109.html', '9-Jan-13', 'Bojanga 1 ind', False, True, '01:53:29', '33ytWu_SdZM'],
               ['/mn-044-jt3-080311.html', '11-Mar-08', 'Joshua Tree 3', False, True, '01:37:38', 'tfC-tBFdwq0'],
               ['/mn-044-dsmc-080722.html', '22-Jul-08', 'DSMC', True, True, '01:23:24', '7lUefVv2p6s'],
               ['/mn-044-jt5-100316.html', '16-Mar-10', 'Joshua Tree 5', False, True, '01:32:08', 'kGHfPMOEAk8'],
               ['/mn-044-bog1-ind-101214.html', '14-Dec-10', 'Bogor 1 ind', False, True, '02:30:31', 'Gc5V2XpPoJc'],
               ['/mn-044-ws-110128.html', '28-Jan-11', 'Winter Series', False, True, '00:57:51', 'rgxMF0ebpYc'],
               ['/mn-044-k1-kor-121110.html', '10-Nov-12', 'Korea 1 kor', False, True, '01:47:42', '1Ab9rUG43Y8'],
               ['/mn-044-k2-kor-121125.html', '25-Nov-12', 'Korea 2 kor', False, True, '01:31:40', 'wpJbh5SpENo'],
               ['/mn-021-boj1-ind-130111.html', '10-Jan-13', 'Bojanga 1 ind', False, True, '02:09:38', 'TlXx1DDpDvQ'],
               ['/mn-044-8fp-jt8-130321.html', '21-Mar-13', 'Joshua Tree 8', False, True, '01:53:18', 'WxobxpjwoTw'],
               ['/mn-046-ana1-091202.html', '2-Dec-09', 'Anaheim 1', True, True, '00:58:49', 'adOlYsVfYDI'],
               ['/mn-048-sea1-070329.html', '29-Mar-07', 'Seattle 1', False, True, '01:29:53', 'y-JAERVoFEM'],
               ['/mn-053-sea1-070326.html', '26-Mar-07', 'Seattle 1', True, True, '01:19:08', 'EC3RscWtjMI'],
               ['/mn-053-dsmc-jul07.html', 'Jul-07', 'DSMC', False, True, '00:59:26', 'M4DEA2lmOhk'],
               ['/mn-053-jt5-100313.html', '13-Mar-10', 'Joshua Tree 5', False, True, '01:03:09', 'lg8hA2sN8QU'],
               ['/mn-053-ws-110119.html', '20-Jan-11', 'Winter Series', False, True, '01:22:34', 'J2yhy2oV2Ps'],
               ['/mn-053-jt6-110313.html', '13-Mar-11', 'Joshua Tree 6', False, True, '01:16:29', 'eN9vYn-PiWk'],
               ['/mn-053-dsmc-120715.html', '15-Jul-12', 'DSMC', False, True, '01:20:56', '_5OTLqxpxcc'],
               ['/mn-059-sea1-070325.html', '25-Mar-07', 'Seattle 1', True, True, '00:51:56', 'xPJyHH2nyI8'],
               ['/mn-059-jt3-080308.html', '8-Mar-08', 'Joshua Tree 3', False, True, '01:35:19', 'SCcjgAcsRc8'],
               ['/mn-059-077-sk-clips-110207-v.html', '7-Feb-11', 'SK', False, True, '00:38:44', 'jFWxq2n6J3c'],
               ['/mn-059-jt6-110308.html', '8-Mar-11', 'Joshua Tree 6', False, True, '01:25:05', '1qJ1j_Zy618'],
               ['/mn-059-dsmc-120616.html', '16-Jun-12', 'DSMC', False, True, '01:16:47', 'yAB28oYRBHQ'],
               ['/mn-059-k2-kor-121120.html', '20-Nov-12', 'Korea 2 kor', False, True, '01:35:02', 'WIovd-z1oCY'],
               ['/mn-059-dsmc-130722.html', '22-Jul-13', 'DSMC', False, True, '01:14:12', '_5OTLqxpxcc'],
               ['/mn-070-jt3-080313.html', '13-Mar-08', 'Joshua Tree 3', False, True, '01:51:37', 'O1h1G5d7aKU'],
               ['/mn-059-077-sk-clips-110207-v.html', '7-Feb-11', 'SK', False, True, '00:38:44', 'jFWxq2n6J3c'],
               ['/mn-077-jt6-110317.html', '17-Mar-11', 'Joshua Tree 6', False, True, '01:47:11', '3mp-Qiv3-tw'],
               ['/mn-095-jt4-090307.html', '07-Mar-09', 'Joshua Tree 4', False, True, '01:12:51', '853ZQGXzXNk'],
               ['/mn-095-jt5-100318.html', '18-Mar-10', 'Joshua Tree 5', False, True, '01:18:41', '63u3_QhMoOs'],
               ['/mn-095-ws-110212.html', '12-Feb-11', 'Winter Series', False, True, '01:01:47', 'nfV1XLCJfN4'],
               ['/mn-106-jt5-100314.html', '14-Mar-10', 'Joshua Tree 5', False, True, '01:16:17', 'PmN1WdcHWWs'],
               ['/mn-106-ws-110203.html', '3-Feb-11', 'Winter Series', False, True, '00:51:55', '1h4DesLkv5g'],
               ['/mn-106-jt6-110318.html', '18-Mar-11', 'Joshua Tree 6', False, True, '01:18:24', 'viBEBzlrasU'],
               ['/mn-106-dsmc-130731.html', '31-Jul-13', 'DSMC', False, True, '00:48:23', '_5OTLqxpxcc'],
               ['/mn-107-sea1-070327.html', '27-Mar-07', 'Seattle 1', True, True, '01:18:34', 'eG_c2VT36Ro'],
               ['/mn-107-dsmc-130710.html', '10-Jul-13', 'DSMC', False, True, '01:22:15', '_5OTLqxpxcc'],
               ['/mn-111-cym1-071123.html', '23-Nov-07', 'Chuang Yen M.', True, True, '01:53:34', 'l8QEzDJKioY'],
               ['/mn-111-jt3-080304.html', '04-Mar-08', 'Joshua Tree 3', True, True, '01:47:20', 'B5--c66mBxc'],
               ['/mn-111-ana-100328.html', '28-Mar-10', 'Anaheim', True, True, '01:14:22', '_5OTLqxpxcc'],
               ['/mn-111-bog1-ind-101209.html', '9-Dec-10', 'Bogor 1 ind', False, True, '02:03:37', 'm6NfFM1qe_Y'],
               ['/mn-111-ws-110211.html', '11-Feb-11', 'Winter Series', False, True, '01:36:57', 'Tt9yyHQEfhU'],
               ['/mn-111-jt7-120318.html', '18-Mar-12', 'Joshua Tree 7', True, True, '01:57:31', 'umMw8BjjBKc'],
               ['/mn-111-k1-kor-121105.html', '5-Nov-12', 'Korea 1 kor', False, True, '01:35:37', '9j_0aAZxVfE'],
               ['/mn-111-kay1-ind-121221.html', '21-Dec-12', 'K&#257;yagat&#257;sati 1', False, True, '01:58:47', 'h-weme7CqqE'],
               ['/mn-111-boj1-ind-130105.html', '5-Jan-13', 'Bojanga 1', False, True, '01:53:18', '0gAVlxEGWfQ'],
               ['/mn-111-dsmc-130526.html', '26-May-13', 'DSMC', False, True, '00:53:44', '_5OTLqxpxcc'],
               ['/mn-111-dsmc-130817.html', '17-Aug-13', 'DSMC', False, True, '01:06:55', '_92SkwvBxnM'],
               ['/mn-112-ws-110129.html', '29-Jan-11', 'Winter Series', False, True, '00:48:35', 'QXJIzonxZc4'],
               ['/mn-113-ws-110121.html', '21-Jan-11', 'Winter Series', False, True, '01:18:28', '495itF-Xkl8'],
               ['/mn-113-k1-kor-121112.html', '12-Nov-12', 'Korea 1 kor', False, True, '00:48:37', 'dp70Bk0n2NM'],
               ['/mn-113-k2-kor-121127.html', '27-Nov-12', 'Korea 2 kor', False, True, '00:26:39', 'GXHrznhh9UE'],
               ['/mn-113-kay1-ind-121226.html', '26-Dec-12', 'K&#257;yagat&#257;sati 1ind', False, True, '01:22:54', 'EKQT10l0qDM'],
               ['/mn-113-dsmc-130719.html', '19-Jul-13', 'DSMC', False, True, '00:57:36', '_92SkwvBxnM'],
               ['/mn-117-cym1-071126.html', '26-Nov-07', 'Chuang Yen M.', False, True, '01:38:39', '1_QgUVHXlyY'],
               ['/mn-119-kay1-ind-121227.html', '27-Dec-12', 'K&#257;yagat&#257;sati 1 ind', False, True, '02:18:45', 'GpD4Z5XGGfA'],
               ['/mn-121-sea1-070403.html', '03-Apr-07', 'Seattle 1', True, True, '01:03:51', '09o3wxG8-b4'],
               ['/mn-121-jt5-100317.html', '17-Mar-10', 'Joshua Tree 5', True, True, '00:59:48', 'IPl8K7rf7JE'],
               ['/mn-121-ws-110130.html', '30-Jan-11', 'Winter Series', False, True, '00:49:12', 'n6FYSULTvco'],
               ['/mn-121-jt8-130322.html', '22-Mar-13', 'Joshua Tree 8', False, True, '01:24:06', 'nsNJhpUDA8A'],
               ['/mn-128-sea1-070402.html', '02-Apr-07', 'Seattle 1', False, True, '01:21:28', 'nl25xR-dqEs'],
               ['/mn-128-ws-110131.html', '31-Jan-11', 'Winter Series', False, True, '00:44:21', 'mTtyy5A6wJk'],
               ['/mn-128-jt6-110311.html', '11-Mar-11', 'Joshua Tree 6', False, True, '01:29:02', 'uycF_2BJL9A'],
               ['/mn-128-jt7-120321.html', '21-Mar-12', 'Joshua Tree 7', False, True, '02:03:36', '5eiSg4m1bfU'],
               ['/mn-133-ana1-091204.html', '4-Dec-09', 'Anaheim 1', True, True, '01:35:58', 'dVJNLve6dqI'],
               ['/mn-135-sea1-070331.html', '31-Mar-07', 'Seattle 1', True, True, '01:05:18', '2NKoEZ9DO9U'],
               ['/mn-135-jt4-090308.html', '08-Mar-09', 'Joshua Tree 4', False, True, '01:05:01', 'FT_td0kswlQ'],
               ['/mn-135-ana1-091203.html', '03-Dec-09', 'Anaheim 1', False, True, '01:38:16', 'rPjZq9cL_hk'],
               ['/mn-135-dsmc-130603.html', '3-Jun-13', 'DSMC', False, True, '00:57:05', '7-WsxHKUhPU'],
               ['/mn-135-dsmc-130730.html', '30-Jul-13', 'DSMC', False, True, '01:05:34', '_5OTLqxpxcc'],
               ['/mn-136-ws-110202.html', '2-Feb-11', 'Winter Series', False, True, '00:41:05', 'ZYs0eUk039Y'],
               ['/mn-140-ws-110122.html', '22-Jan-11', 'Winter Series', False, True, '01:18:28', '4EIYSAWVSlM'],
               ['/mn-140-dsmc-130801.html', '1-Aug-13', 'DSMC', False, True, '00:49:23', '_5OTLqxpxcc'],
               ['/mn-148-cym1-071125.html', '25-Nov-07', 'Chuang Yen M.', False, True, '01:29:10', 'J5VAYrByPcs'],
               ['/mn-148-jt3-080307.html', '7-Mar-08', 'Joshua Tree 3', False, True, '01:07:53', '39EYKO3fPQg'],
               ['/mn-148-jt7-sk-120320-v.html', '22-Mar-12', 'Joshua Tree 7  SK', False, True, '01:06:35', 'BqWkpyygcZw'],
               ['/mn-148-k2-kor-121124.html', '24-Nov-12', 'Korea 2 kor', False, True, '00:58:05', 'L4LCGDTSuvU'],
               ['/mn-148-kay1-ind-bi-121225.html', '25-Dec-12', 'K&#257;yagat&#257;sati 1 ind', False, True, '01:00:30', 'o4NyMMKe8Ak'],
               ['/mn-021-152-jt5-100319.html', '10-Mar-10', 'Joshua Tree 5', True, True, '00:40:45', 'SLJ7YKSY_b0'],
               ['/mn-152-ws-110117.html', '17-Jan-11', 'Winter Series', False, True, '00:40:22', 'gUOIaSJcTHw'],
               ['/mn-152-jt7-120323.html', '23-Mar-12', 'Joshua Tree 7', False, True, '01:40:49', 'ZP_fNEKUhCY']]

sets = [
        ['DSMC', 'dsmc'],
        ['Joshua Tree 1', 'jt1'],
        ['Joshua Tree 2', 'jt2'],
        ['Joshua Tree 3', 'jt3'],
        ['Joshua Tree 4', 'jt4'],
        ['Joshua Tree 5', 'jt5'],
        ['Joshua Tree 6', 'jt6'],
        ['Joshua Tree 7', 'jt7'],
        ['Joshua Tree 8', 'jt8'],
        ['Korea 1 kor', 'k1-kor'],
        ['Korea 2 kor', 'k2-kor'],
        ['San Diego', 'sand'],
        ['Winter Series', 'ws']]

addonDev = True
if not addonDev:
    import sys
    argv = sys.argv
import os
import sqlite3 as lite
import urllib
import urllib.parse as urlparse
import xbmc 
import xbmcgui
import xbmcplugin
import xml.dom.minidom as minidom

def getText(node):
    rc= []
    for node in node.childNodes:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def build_url(query):
    return base_url + '?' + urllib.parse.urlencode(query)

def makeXbmcMenu(menuContent):
    for elem in menuContent:
        urlTags, parameters, addonInfo = elem[0], elem[1], elem[2]
        url = build_url(urlTags)
        isFolder = parameters.pop('isFolder')
        if parameters.get('iconImage', None) == None:
            parameters['iconImage'] = 'defaultFolder.png' if isFolder else 'DefaultVideo.png' 
        li = xbmcgui.ListItem(**parameters)
        li.setProperty('IsPlayable', 'false' if isFolder else 'true')
        if addonInfo:
            li.setInfo(**addonInfo)
            li.addContextMenuItems([('Video Information', 'XBMC.Action(Info)')]) 
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=isFolder)
    xbmcplugin.endOfDirectory(addon_handle)


def getSelectionKey(selection, typeSel):
    if typeSel == 'Teachings': return selection[:2].lower() + '-' + (3 - len(selection[3:]))*'0' + selection[3:]
    if typeSel == 'Series': return '-' + selection + '-'
    
def getUserInput(defaultSearch):
    exit = True 
    while (exit):
        kb = xbmc.Keyboard('default', 'heading', True)
        kb.setDefault(defaultSearch)
        kb.setHeading('Entre palabra a buscar en el tema del Sutta')
        kb.setHiddenInput(False)
        kb.doModal()
        if (kb.isConfirmed()):
            name_confirmed  = kb.getText()
            name_correct = name_confirmed.count(' ')
            if (name_correct == 0):
                name = name_confirmed
                exit = False
    return name

# ----------------------------------------------------------------------------
#        Manipulación del archivo favourites.xml
# ----------------------------------------------------------------------------

def getFavouritesContent():
    favContent = []
    favFile = xbmc.translatePath('special://profile/favourites.xml')
    if os.path.isfile(favFile):
        favFile = open(favFile, 'r')
        favXml = favFile.read()
        favFile.close
        favDom = minidom.parseString(favXml)
        favList = favDom.getElementsByTagName('favourite')
        for favourite in favList:
            send_url = getText(favourite)
            favContent.append((dict(favourite.attributes.items()), send_url))
    return favContent

# ----------------------------------------------------------------------------
#        Manejo de las bases de datos
# ----------------------------------------------------------------------------

def getbookmarkBD(base_url):
    bkmkFile = xbmc.translatePath('special://profile/Database/myvideos78.db')
    con = lite.connect(bkmkFile)
    with con:
        cur = con.cursor()
        cur.execute("select bookmark.idFile,timeInSeconds, files.strFilename, type, files.lastPlayed from bookmark, files where bookmark.idFile = files.idFile")
        rows = cur.fetchall()
    return [row for row in rows if row[2].find(base_url) != -1 and row[3] == 1] 

base_url = argv[0]
addon_handle = int(argv[1])
args = urlparse.parse_qs(argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')

menu = args.get('menu', None)

if menu is None:
    menuContent = [
                   [{'menu':'Teachings'}, {'label':'Teachings', 'isFolder':True}, None],
                   [{'menu':'Series'}, {'label':'Series', 'isFolder':True}, None],
                   [{'menu':'Recently Added'}, {'label':'Recently Added', 'isFolder':True}, None],
                   [{'menu':"Bhante's Most Commented"}, {'label':"Bhante's Most Commented", 'isFolder':True}, None],
                   [{'menu':'Favourites'}, {'label':'Favourites', 'isFolder':True}, None],
                   [{'menu':'Search'}, {'label':'Search', 'isFolder':True}, None]
                   ]
    bkmkList = getbookmarkBD(base_url)
    if bkmkList:
        menuContent.append([{'menu':'Paused'}, {'label':'Paused', 'isFolder':True}, None])
    
    makeXbmcMenu(menuContent)
elif menu[0] == 'Teachings':
    menuContent = []
    for elem in index:
        urlTags = {'menu':'suttas', 'selection':elem[0], 'type':'Teachings'}
        parameters = {'isFolder':True, 'label':elem[0] + ' ' + elem[1]}
        addonInfo = {'type':'video', 'infoLabels':{'title':elem[0] + ' ' + elem[1], 'plot':elem[2]}}
        menuContent.append([urlTags, parameters, addonInfo])
    makeXbmcMenu(menuContent)
elif menu[0] == 'Series':
    menuContent = []
    for elem in sets:
        urlTags = {'menu':'suttas', 'selection':elem[1], 'type':'Series'}
        parameters = {'isFolder':True, 'label':elem[0]}        
        menuContent.append([urlTags, parameters, None])
    makeXbmcMenu(menuContent)
elif menu[0] == 'Recently Added':
    sortedTalks = sorted(dhammaTalks, key = lambda elem: elem[0][-11:], reverse = True)
    menuContent = []
    for elem in sortedTalks:
        urlTags = {'menu':'dhammaTalks', 'selection':elem[-1]}
        parameters = {'isFolder':False, 'label':' '.join([elem[0][1:7],elem[1],elem[2]])}
        menuContent.append([urlTags, parameters, None])
    makeXbmcMenu(menuContent)
elif menu[0] == "Bhante's Most Commented":
    sortedTalks = sorted(index, key = lambda elem: elem[-1], reverse = True)
    menuContent = []
    addonInfo = {'type':'video'}
    for elem in sortedTalks:
        urlTags = {'menu':'suttas', 'type':'Teachings', 'selection':elem[0]}
        parameters = {'isFolder':True, 'label':elem[0] + ' ' + elem[1]}
        addonInfo = {'type':'video', 'infoLabels':{'title':elem[0] + ' ' + elem[1], 'plot':elem[2]}}
        menuContent.append([urlTags, parameters, addonInfo])
    makeXbmcMenu(menuContent)
elif menu[0]== 'Favourites':
    favList = getFavouritesContent()
    menuContent = []
    for favAttrib, send_url in favList:
        if send_url.find(base_url) != -1:
            limInf = send_url.find('?') + 1
            limSup = send_url.find('"', limInf)
            args = urlparse.parse_qs(send_url[limInf:limSup])
            for key, value in args.items(): args[key] = value[0]
            isFolder = not 'dhammaTalks' in args.values()                
            name = favAttrib['name']
            menuContent.append([args,{'label':name, 'isFolder':isFolder}, None])
    makeXbmcMenu(menuContent)
elif menu[0]== 'Search':
    wordToSearch = getUserInput('')
    menuContent = []
    for elem in index:
        if wordToSearch in elem[2]:
            urlTags = {'menu':'suttas', 'selection':elem[0], 'type':'Teachings'}
            parameters = {'isFolder':True, 'label':elem[0] + ' ' + elem[1]}
            menuContent.append([urlTags, parameters, None])
    makeXbmcMenu(menuContent)
elif menu[0]== 'Paused':
    menuContent = []
    bkmkList = getbookmarkBD(base_url)
    for row in bkmkList:
        row_url = row[2]
        limInf = row_url.find('?') + 1
        args = urlparse.parse_qs(row_url[limInf:])
        for key, value in args.items(): args[key] = value[0]
        for elem in dhammaTalks:
            if elem[-1] == args['selection']: break
        name = ' '.join([elem[0][1:7], elem[1], elem[2], '   (' + row[-1] + ')'])
        menuContent.append([args, {'label':name, 'isFolder':False}, None])
    makeXbmcMenu(menuContent)    
elif menu[0] == 'suttas':
    selection = args.get('selection')[0]
    typeSel = args.get('type')[0]
    selectionKey = getSelectionKey(selection, typeSel)
    selection = selection[:2].lower() + '-' + (3 - len(selection[3:]))*'0' + selection[3:]
    sortedTalks = sorted(dhammaTalks, key = lambda elem: elem[0][-11:], reverse = False)
    menuContent = []
#     p = HTMLParser()
    for elem in sortedTalks:
        if selectionKey in elem[0]:
            urlTags = {'menu':'dhammaTalks', 'selection':elem[-1]}
            parameters = {'label':' '.join([elem[0][1:7],elem[1],elem[2]]), 'isFolder':False}
            menuContent.append([urlTags, parameters, None])
    makeXbmcMenu(menuContent)
elif menu[0] == 'dhammaTalks':
    selection = args.get('selection')[0]
    url = 'plugin://plugin.video.youtube/?path=root/video&action=play_video&videoid=' + selection 
    li = xbmcgui.ListItem(path = url)
    li.setProperty('IsPlayable', 'true')
    li.setProperty('mimetype', 'video/x-msvideo')
    xbmcplugin.setResolvedUrl(handle = addon_handle, succeeded=True, listitem=li)