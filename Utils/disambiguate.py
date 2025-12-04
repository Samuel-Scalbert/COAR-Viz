from app.app import db
from rapidfuzz import fuzz
from flask import url_for


def disambiguate_from_software(software):
    query = f'''
                for software in softwares
                return distinct software.software_name.rawForm
                '''
    list_software = list(db.AQLQuery(query, rawResults=True, batchSize=2000))
    list_possible_dup_docid = []
    list_possible_dup = [software]
    for software_available in list_software:
        ratio = fuzz.ratio(software_available, software)
        if software != software_available and ratio > 50:
            token_ratio = fuzz.token_sort_ratio(software, software_available)
            partial_ratio = fuzz.partial_ratio(software_available, software)
            average_ratio = (token_ratio+partial_ratio+ratio)/3
            if average_ratio > 80:
                list_possible_dup.append(software_available)
            if partial_ratio >= 100:
                list_possible_dup.append(software_available)
    for software in list_possible_dup:
        query = f'''
                    for software in softwares
                        filter software.software_name.rawForm == '{software}'
                        for edge in edge_doc_to_software
                            filter edge._to == software._id
                            let doc = document(edge._from)
                            return distinct doc._key
                    '''
        result_software = list(db.AQLQuery(query, rawResults=True, batchSize=2000))
        for result_docid in result_software:
            list_possible_dup_docid.append([software, result_docid])
    return list_possible_dup_docid

def fetch_for_software(softwareName, docid):
    query = f'''
                LET docId = "documents/{docid}"
                
                // -----------------------------------
                // DOCUMENT INFO
                // -----------------------------------
                LET docInfo = (
                    LET d = DOCUMENT(docId)
                    RETURN {{
                        file_hal_id: d.file_hal_id,
                        date: d.date,
                        title: d.title
                    }}
                )
                
                // -----------------------------------
                // SOFTWARE (NOT DISTINCT — preserve context)
                // -----------------------------------
                LET software = (
                    FOR edge IN edge_doc_to_software
                        FILTER edge._from == docId
                        LET sw = DOCUMENT(edge._to)
                        FILTER sw.software_name.normalizedForm == "{softwareName}"
                        RETURN {{
                            name: sw.software_name.rawForm,
                            context: sw.context
                        }}
                )
                
                //////////////////////////////
                // URL (DISTINCT)
                //////////////////////////////
                LET url = (
                    FOR edge IN edge_doc_to_software
                        FILTER edge._from == docId
                        LET sw = DOCUMENT(edge._to)
                        FILTER sw.software_name.normalizedForm == "{softwareName}"
                        FILTER sw.url.rawForm != null && sw.url.rawForm != ""
                        COLLECT urlValue = sw.url.rawForm
                        RETURN urlValue
                )
                
                
                // -----------------------------------
                // Verified
                // -----------------------------------
                LET verification_by_author = (
                    FOR edge IN edge_doc_to_software
                        FILTER edge._from == docId
                        LET sw = DOCUMENT(edge._to)
                        FILTER sw.verification_by_author in [true, false]
                        FILTER sw.software_name.normalizedForm == "{softwareName}"
                        return distinct sw.verification_by_author
                )

                
                // -----------------------------------
                // STRUCTURES (DISTINCT)
                // -----------------------------------
                LET structures = (
                    FOR edge IN edge_doc_to_struc
                        FILTER edge._from == docId
                        LET s = DOCUMENT(edge._to)
                        filter s.type in ["researchteam","department","laboratory"]
                        COLLECT      /* DISTINCT */
                            id = s.id_haureal,
                            name = s.name,
                            acr = s.acronym || "None"
                        RETURN {{
                            id_haureal: id,
                            name,
                            acronym: acr
                        }}
                )
                
                // -----------------------------------
                // AUTHORS (DISTINCT)
                // -----------------------------------
                LET authors = (
                    FOR edge IN edge_doc_to_author
                        FILTER edge._from == docId
                        LET a = DOCUMENT(edge._to)
                        LET fullName = CONCAT(a.name.forename, " ", a.name.surname)
                        COLLECT     /* DISTINCT */
                            full = fullName,
                            authorId = a.id.halauthorid
                        RETURN {{
                            name: full,
                            halAuthorId: authorId
                        }}
                )
                
                // -----------------------------------
                // FINAL STRUCTURED RESULT
                // -----------------------------------
                RETURN {{
                    document: FIRST(docInfo),
                    software,
                    authors,
                    structures,
                    url: url,
                    verification: verification_by_author
                }}
                '''
    data_software = db.AQLQuery(query, rawResults=True, batchSize=2000)
    return data_software[0]