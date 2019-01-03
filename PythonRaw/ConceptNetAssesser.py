import pandas as pd
import requests
from neo4j.v1 import GraphDatabase

requests.adapters.DEFAULT_RETRIES=5

class Neo4jGraphDB(object):

    def __init__(self, uri):
        self._driver = GraphDatabase.driver(uri, auth=('neo4j', 'tisiri123'), encrypted=False)

    def close(self):
        self._driver.close()

    def insertUniqueRelation(self, term1, term2, relationName):
        with self._driver.session() as session:
            relation = session.write_transaction(self._create_relation, term1, term2, relationName)

    @staticmethod
    def _create_relation(tx, term1, term2, relationName):
        result = tx.run("MERGE (t1:"+term1+") MERGE (t2: "+term2+") MERGE (t1)-[r: "+relationName+"]->(t2) RETURN r")
        return result.single()[0]


df = pd.read_csv('twoColumnsOrdered.csv')
df2 = pd.DataFrame(columns=["term1","term2","relation"])
graph = Neo4jGraphDB("bolt://127.0.0.1:7687")
terms = set()
for row in df.iterrows():
    obj = requests.get('http://api.conceptnet.io/c/pt/'+row[1][0].strip()).json()
    for r in obj['edges']:
##        print(r['end']['label'])
##        print(row[1][1].strip())
        
        if(r['end']['label'] == row[1][1].strip()):
            tup = tuple([row[1][0], r['end']['label'],r['rel']['label']])
            
            #rint(row[1][0],' -[',r['rel']['label'],']->',r['end']['label'])
            if(tup not in terms):
                graph.insertUniqueRelation(row[1][0].strip(), r['end']['label'],r['rel']['label'])
                rel = pd.DataFrame([[row[1][0].strip(), r['end']['label'], r['rel']['label']],], columns=["term1","term2","relation"])
                df2=df2.append(rel)
                terms.add(tup)
                print(tup)
            
df2.to_csv('MappedRelations.csv')
