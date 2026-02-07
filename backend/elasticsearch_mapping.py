def get_index_mapping() -> dict:
    return {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "analyzer": {
                    "default": {
                        "type": "standard"
                    },
                    "title_analyzer": {
                        "type": "standard",
                        "stopwords": "_english_"
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "nct_id": {"type": "keyword"},
                "study_first_submitted_date": {"type": "date"},
                "last_update_submitted_date": {"type": "date"},
                "last_update_posted_date": {"type": "date"},
                "start_date": {"type": "date"},
                "completion_date": {"type": "date"},
                "primary_completion_date": {"type": "date"},
                "results_first_posted_date": {"type": "date"},

                "brief_title": {
                    "type": "text",
                    "analyzer": "title_analyzer",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 512}}
                },
                "official_title": {
                    "type": "text",
                    "analyzer": "title_analyzer",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 512}}
                },
                "acronym": {"type": "keyword"},
                "overall_status": {"type": "keyword"},
                "phase": {"type": "keyword"},
                "study_type": {"type": "keyword"},
                "enrollment": {"type": "integer"},
                "enrollment_type": {"type": "keyword"},
                "condition_names": {
                    "type": "keyword",
                    "fields": {"text": {"type": "text", "analyzer": "standard"}}
                },
                "sponsor_names": {"type": "keyword"},
                "source": {"type": "keyword"},
                "facility_countries": {"type": "keyword"},
                "facility_states": {"type": "keyword"},
                "facility_cities": {"type": "keyword"},
                "gender": {"type": "keyword"},
                "minimum_age": {"type": "keyword"},
                "maximum_age": {"type": "keyword"},
                "age_categories": {"type": "keyword"},
                "healthy_volunteers": {"type": "boolean"},
                "brief_summaries_description": {
                    "type": "text",
                    "analyzer": "standard"
                },
                "detailed_description": {
                    "type": "text",
                    "analyzer": "standard",
                    "index": False
                },
                "conditions": {"type": "object", "enabled": False},
                "sponsors": {"type": "object", "enabled": False},
                "facilities": {"type": "object", "enabled": False},
                "design_outcomes": {"type": "object", "enabled": False},
                "age": {"type": "object", "enabled": False},
                "id_information": {"type": "object", "enabled": False},
                "allocation": {"type": "keyword"},
                "intervention_model": {"type": "keyword"},
                "primary_purpose": {"type": "keyword"},
                "masking": {"type": "keyword"},
                "has_dmc": {"type": "float"},
                "has_results": {"type": "boolean"},
                "number_of_arms": {"type": "keyword"},
                "target_duration": {"type": "keyword"},
            }
        }
    }