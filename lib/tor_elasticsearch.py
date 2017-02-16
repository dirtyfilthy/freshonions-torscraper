import os
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import DocType, Date, Nested, Boolean
from elasticsearch_dsl import analyzer, InnerObjectWrapper, Completion, Keyword, Text

def is_elasticsearch_enabled():
    return (os.environ['ELASTICSEARCH_ENABLED'] and os.environ['ELASTICSEARCH_ENABLED'].lower()=='true')

class DomainDocType(DocType):
    title = Text()
    created_at = Date()
    visited_at = Date()
    last_alive = Date()
    is_up      = Boolean()
    is_fake    = Boolean()
    is_genuine = Boolean()
    is_crap    = Boolean()
    url        = Text()
    is_subdomain = Boolean()
    ssl        = Boolean()
    port       = Integer()

    class Meta:
        name = 'domain'
        doc_type = 'domain'
        index = 'hiddenservices'

    @classmethod
    def get_indexable(cls):
        return cls.get_model().get_objects()

    @classmethod
    def from_obj(klass, obj):
        return klass(
            meta={'id': obj.host}
            title=obj.title,
            created_at=obj.created_at,
            visited_at=obj.visited_at,
            is_up=obj.is_up,
            is_fake=obj.is_fake,
            is_genuine=obj.is_fake,
            is_crap=obj.is_crap,
            url=obj.index_url(),
            is_subdomain=obj.is_subdomain,
            ssl=obj.ssl,
            port=port
        )

    @classmethod
    def set_isup(klass, obj, is_up):
    	dom = klass(meta={'id': obj.host})
    	dom.update(is_up=is_up)





class PageDocType(DocType):

	html_strip = analyzer('html_strip', 
		tokenizer="standard",
    	filter=["standard", "lowercase", "stop", "snowball"],
    	char_filter=["html_strip"]
	)

    title = Text()
    created_at = Date(analyzer="snowball")
    visited_at = Date()
    code       = Integer()
    body       = Text(analyzer=html_strip)

    class Meta:
        name = 'page'
        index = 'hiddenservices'
        doc_type = 'page'
        parent = MetaField(type='domain')

    @classmethod
    def get_indexable(cls):
        return cls.get_model().get_objects()

    @classmethod
    def from_obj(klass, obj, body):
        return klass(
            meta={'id':obj.url, 'routing':obj.domain.host}
            title=obj.title,
            created_at=obj.created_at,
            visited_at=obj.visited_at,
            code=obj.code,
            body=body
        )

if is_elasticsearch_enabled():
    connections.create_connection(hosts=[os.environ['ELASTICSEARCH_HOST']], timeout=20)