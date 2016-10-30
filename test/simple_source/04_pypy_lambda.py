# Bug #16 reported by alexwlchan via hypothesis
# in xdis 3.2.0 we weren't LOAD_METHOD wasn't tagged as
# a name op
f = lambda right: [].map(lambda length:())
