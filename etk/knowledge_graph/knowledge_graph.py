from typing import Dict, List
from etk.knowledge_graph.schema import KGSchema
from etk.etk_exceptions import KGValueError, UndefinedFieldError
from etk.knowledge_graph.graph import Graph
from etk.knowledge_graph.triples import Triples
from etk.knowledge_graph.node import URI, Literal
import json
from etk.utilities import deprecated


class KnowledgeGraph(Graph):
    """
    This class is a knowledge graph object, provides API for user to construct their kg.
    Add field and value to the kg object, analysis on provenance
    """
    def __init__(self, schema: KGSchema, doc):
        super().__init__()
        self.origin_doc = doc
        self.schema = schema
        self._fork_namespace_manager()

    @deprecated()
    def add_value(self, field_name: str, value: object=None) -> None:
        """
        Add a value to knowledge graph.
        Input can either be a value or a json_path. If the input is json_path, the helper function _add_doc_value is
        called.
        If the input is a value, then it is handled

        Args:
            field_name: str, the field name in the knowledge graph
            value: the value to be added to the knowledge graph
        """
        if not self._ns.store.namespace(''):
            self.bind(None, 'http://isi.edu/default-ns/')
        obj = self.schema.field_type(field_name, value)
        if not obj:
            raise Exception()
        self.add_triple(URI(self.origin_doc.doc_id), URI(field_name), obj)

    def _find_types(self, triples):
        """
        find type in root level
        :param triples:
        :return:
        """
        types = []
        for t in triples:
            s, p, o = t
            if self._is_rdf_type(p):
                if isinstance(o, Triples):
                    continue
                types.append(o)
        return types

    def add_triples(self, triples, context=None):
        if not context:
            context = set([])
        s_types = self._find_types(triples)

        for t in triples:
            s, p, o = t
            o_types = []
            if isinstance(o, Triples) and o not in context:
                context.add(o)
                self.add_triples(o, context)
                o_types = self._find_types(o)

            if self.schema.is_valid(s_types, p, o_types):
                triple = self._convert_triple_rdflib((s, p, o))
                self._g.add(triple)

    @property
    def value(self) -> Dict:
        """
        Get knowledge graph object
        """
        g = {}
        for p, o in self._g.predicate_objects():
            _, property_ = self._ns.split_uri(p)
            if property_ not in g:
                g[property_] = list()
            g[property_].append({
                'key': self.create_key_from_value(o, property_),
                'value': o
            })
        return g

    @deprecated()
    def get_values(self, field_name: str) -> List[object]:
        """
        Get a list of all the values of a field.
        """
        result = list()
        p = self.schema.parse_field(field_name)
        for o in self._g.objects(None, p):
            result.append(o.toPython())
        return result

    def create_key_from_value(self, value, field_name: str):
        key = self.schema.field_type(field_name, value)
        if isinstance(key, URI):
            return key
        if isinstance(key, str) or isinstance(key, Literal):
            key = str(key).strip().lower()
        return key

    def serialize(self, format='legacy', namespace_manager=None):
        if format == 'legacy':
            # Output DIG format
            return json.dumps(self.value)
        return super().serialize(format, namespace_manager)

    def _fork_namespace_manager(self):
        for prefix, ns in self.schema.ontology._ns.namespaces():
            self.bind(prefix, ns)
