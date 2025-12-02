from src.infra.db import run_query
from src.schemas.schemas import OriginDateFilter, YearFilter, YearRangeFilter


def fetch_process_count():
    sql = """
        SELECT COUNT(*) AS total_processos
        FROM PRO_PROCESSO_VALENCA
    """
    return run_query(sql)

def fetch_by_origin():
    sql = """
        SELECT COUNT(*) AS total,
               T02.DES_ATRIBUTO AS origin
        FROM PRO_PROCESSO_VALENCA T01
        INNER JOIN DAR_DOMINIO_ATRIBUTO_VALENCA T02
            ON T01.TIP_ORIGEM_PROCESSO = T02.VAL_ATRIBUTO
           AND T02.NOM_ATRIBUTO = 'TIP_ORIGEM_PROCESSO'
        GROUP BY T02.DES_ATRIBUTO
        ORDER BY total DESC
    """
    return run_query(sql)

def fetch_by_status():
    sql = """
        SELECT COUNT(*) AS total,
               T02.DES_ATRIBUTO AS status
        FROM PRO_PROCESSO_VALENCA T01
        INNER JOIN DAR_DOMINIO_ATRIBUTO_VALENCA T02
            ON T01.STA_PROCESSO = T02.VAL_ATRIBUTO
           AND T02.NOM_ATRIBUTO = 'STA_PROCESSO'
        GROUP BY T02.DES_ATRIBUTO
        ORDER BY T02.DES_ATRIBUTO
    """
    return run_query(sql)

def fetch_by_matter():
    sql = """
        SELECT COUNT(*) AS total,
               COALESCE(T02.NOM_MATERIA, 'Não informado') AS subject
        FROM PRO_PROCESSO_VALENCA T01
        LEFT JOIN MAT_MATERIA_VALENCA T02
            ON T01.ISN_MATERIA = T02.ISN_MATERIA
        GROUP BY T02.NOM_MATERIA
        ORDER BY T02.NOM_MATERIA
    """
    return run_query(sql)

def fetch_by_group():
    sql = """
        SELECT COUNT(*) AS total,
               COALESCE(T02.DSC_GRUPO_PROCESSO, 'Não informado') AS process_group
        FROM PRO_PROCESSO_VALENCA T01
        LEFT JOIN GPP_GRUPO_PROCESSO_VALENCA T02
            ON T01.ISN_GRUPO_PROCESSO = T02.ISN_GRUPO_PROCESSO
        GROUP BY T02.DSC_GRUPO_PROCESSO
        ORDER BY T02.DSC_GRUPO_PROCESSO
    """
    return run_query(sql)

def fetch_by_organization():
    sql = """
        SELECT COUNT(*) AS total,
               COALESCE(T03.DSC_ORGAO, 'Não informado') AS agency
        FROM PRO_PROCESSO_VALENCA T01
        LEFT JOIN INS_INSTANCIA_VALENCA T02
            ON T01.ISN_PROCESSO = T02.ISN_PROCESSO
        LEFT JOIN ORG_ORGAO_VALENCA T03
            ON T02.ISN_ORGAO = T03.ISN_ORGAO
        GROUP BY T03.DSC_ORGAO
        ORDER BY T03.DSC_ORGAO
    """
    return run_query(sql)

def fetch_by_origin_with_instance_date_filter(filters: OriginDateFilter):
    sql = f"""
        SELECT 
            COUNT(1) AS [Quantidade],
            T02.DES_ATRIBUTO AS [Origem]
        FROM PRO_PROCESSO_VALENCA T01
        INNER JOIN DAR_DOMINIO_ATRIBUTO_VALENCA T02 
            ON T01.TIP_ORIGEM_PROCESSO = T02.VAL_ATRIBUTO
        AND T02.NOM_ATRIBUTO = 'TIP_ORIGEM_PROCESSO'
        LEFT JOIN INS_INSTANCIA_VALENCA T03 
            ON T01.ISN_PROCESSO = T03.ISN_PROCESSO
        CROSS APPLY (
            SELECT TRY_CONVERT(
                date, NULLIF(LTRIM(RTRIM(T03.DAT_INSTANCIA)), '')
            ) AS DAT_INSTANCIA_DT
        ) AS X
        WHERE X.DAT_INSTANCIA_DT IS NOT NULL
        AND X.DAT_INSTANCIA_DT >= '{filters.start_date}'
        AND X.DAT_INSTANCIA_DT <= '{filters.end_date}'
        GROUP BY 
            T02.DES_ATRIBUTO
        ORDER BY 
            T02.DES_ATRIBUTO
    """
    return run_query(sql)

def fetch_by_origin_registration_by_year_range(filters: YearRangeFilter):
    # Gerar a lista de anos dinamicamente baseada no intervalo
    years_union = " UNION ALL ".join(
        [f"SELECT {year} AS Ano" for year in range(
            filters.start_year, filters.end_year + 1
        )])
    
    sql = f"""
        WITH Base AS (
            SELECT 
                YEAR(TRY_CONVERT(date, T03.DAT_INSTANCIA)) AS Ano
            FROM PRO_PROCESSO_VALENCA T01
            INNER JOIN DAR_DOMINIO_ATRIBUTO_VALENCA T02 
                ON T01.TIP_ORIGEM_PROCESSO = T02.VAL_ATRIBUTO
               AND T02.NOM_ATRIBUTO = 'TIP_ORIGEM_PROCESSO'
            LEFT JOIN INS_INSTANCIA_VALENCA T03 
                ON T01.ISN_PROCESSO = T03.ISN_PROCESSO
            WHERE TRY_CONVERT(date, T03.DAT_INSTANCIA) IS NOT NULL
              AND T02.DES_ATRIBUTO = 'Cadastro'
        ),
        Anos AS (
            {years_union}
        )
        SELECT 
            A.Ano,
            ISNULL(B.Total, 0) AS TotalCadastro
        FROM Anos A
        LEFT JOIN (
            SELECT Ano, COUNT(*) AS Total
            FROM Base
            GROUP BY Ano
        ) B ON A.Ano = B.Ano
        ORDER BY A.Ano
    """
    return run_query(sql)

def fetch_by_origin_registration_last_six_months(filters: YearFilter):
    sql = f"""
        WITH Base AS (
            SELECT 
                TRY_CONVERT(date, T03.DAT_INSTANCIA) AS DataInstancia,
                MONTH(TRY_CONVERT(date, T03.DAT_INSTANCIA)) AS Mes,
                YEAR(TRY_CONVERT(date, T03.DAT_INSTANCIA)) AS Ano
            FROM PRO_PROCESSO_VALENCA T01
            INNER JOIN DAR_DOMINIO_ATRIBUTO_VALENCA T02 
                ON T01.TIP_ORIGEM_PROCESSO = T02.VAL_ATRIBUTO
               AND T02.NOM_ATRIBUTO = 'TIP_ORIGEM_PROCESSO'
            LEFT JOIN INS_INSTANCIA_VALENCA T03 
                ON T01.ISN_PROCESSO = T03.ISN_PROCESSO
            WHERE TRY_CONVERT(date, T03.DAT_INSTANCIA) IS NOT NULL
              AND T02.DES_ATRIBUTO = 'Cadastro'
              AND YEAR(TRY_CONVERT(date, T03.DAT_INSTANCIA)) = {filters.year}
        ),
        Meses AS (
            SELECT 7 AS Mes
            UNION ALL SELECT 8
            UNION ALL SELECT 9
            UNION ALL SELECT 10
            UNION ALL SELECT 11
            UNION ALL SELECT 12
        )
        SELECT 
            M.Mes,
            DATENAME(MONTH, DATEFROMPARTS({filters.year}, M.Mes, 1)) AS NomeMes,
            ISNULL(C.Total, 0) AS TotalCadastro
        FROM Meses M
        LEFT JOIN (
            SELECT Mes, COUNT(*) AS Total
            FROM Base
            GROUP BY Mes
        ) C ON M.Mes = C.Mes
        ORDER BY M.Mes
    """
    return run_query(sql)

def fetch_by_origin_capture_last_six_months(filters: YearFilter):
    sql = f"""
        WITH Base AS (
            SELECT 
                TRY_CONVERT(date, T03.DAT_INSTANCIA) AS DataInstancia,
                MONTH(TRY_CONVERT(date, T03.DAT_INSTANCIA)) AS Mes,
                YEAR(TRY_CONVERT(date, T03.DAT_INSTANCIA)) AS Ano
            FROM PRO_PROCESSO_VALENCA T01
            INNER JOIN DAR_DOMINIO_ATRIBUTO_VALENCA T02 
                ON T01.TIP_ORIGEM_PROCESSO = T02.VAL_ATRIBUTO
               AND T02.NOM_ATRIBUTO = 'TIP_ORIGEM_PROCESSO'
            LEFT JOIN INS_INSTANCIA_VALENCA T03 
                ON T01.ISN_PROCESSO = T03.ISN_PROCESSO
            WHERE TRY_CONVERT(date, T03.DAT_INSTANCIA) IS NOT NULL
              AND T02.DES_ATRIBUTO = 'Captura'
              AND YEAR(TRY_CONVERT(date, T03.DAT_INSTANCIA)) = {filters.year}
        ),
        Meses AS (
            SELECT 7 AS Mes
            UNION ALL SELECT 8
            UNION ALL SELECT 9
            UNION ALL SELECT 10
            UNION ALL SELECT 11
            UNION ALL SELECT 12
        )
        SELECT 
            M.Mes,
            DATENAME(MONTH, DATEFROMPARTS({filters.year}, M.Mes, 1)) AS NomeMes,
            ISNULL(C.Total, 0) AS TotalCaptura
        FROM Meses M
        LEFT JOIN (
            SELECT Mes, COUNT(*) AS Total
            FROM Base
            GROUP BY Mes
        ) C ON M.Mes = C.Mes
        ORDER BY M.Mes
    """
    return run_query(sql)

def fetch_by_origin_distribution_last_six_months(filters: YearFilter):
    sql = f"""
        WITH Base AS (
            SELECT 
                TRY_CONVERT(date, T03.DAT_INSTANCIA) AS DataInstancia,
                MONTH(TRY_CONVERT(date, T03.DAT_INSTANCIA)) AS Mes,
                YEAR(TRY_CONVERT(date, T03.DAT_INSTANCIA)) AS Ano
            FROM PRO_PROCESSO_VALENCA T01
            INNER JOIN DAR_DOMINIO_ATRIBUTO_VALENCA T02 
                ON T01.TIP_ORIGEM_PROCESSO = T02.VAL_ATRIBUTO
               AND T02.NOM_ATRIBUTO = 'TIP_ORIGEM_PROCESSO'
            LEFT JOIN INS_INSTANCIA_VALENCA T03 
                ON T01.ISN_PROCESSO = T03.ISN_PROCESSO
            WHERE TRY_CONVERT(date, T03.DAT_INSTANCIA) IS NOT NULL
              AND T02.DES_ATRIBUTO = 'Distribuição'
              AND YEAR(TRY_CONVERT(date, T03.DAT_INSTANCIA)) = {filters.year}
        ),
        Meses AS (
            SELECT 7 AS Mes
            UNION ALL SELECT 8
            UNION ALL SELECT 9
            UNION ALL SELECT 10
            UNION ALL SELECT 11
            UNION ALL SELECT 12
        )
        SELECT 
            M.Mes,
            DATENAME(MONTH, DATEFROMPARTS({filters.year}, M.Mes, 1)) AS NomeMes,
            ISNULL(C.Total, 0) AS TotalDistribuicao
        FROM Meses M
        LEFT JOIN (
            SELECT Mes, COUNT(*) AS Total
            FROM Base
            GROUP BY Mes
        ) C ON M.Mes = C.Mes
        ORDER BY M.Mes
    """
    return run_query(sql)

def fetch_by_origin_import_last_six_months(filters: YearFilter):
    sql = f"""
        WITH Base AS (
            SELECT 
                TRY_CONVERT(date, T03.DAT_INSTANCIA) AS DataInstancia,
                MONTH(TRY_CONVERT(date, T03.DAT_INSTANCIA)) AS Mes,
                YEAR(TRY_CONVERT(date, T03.DAT_INSTANCIA)) AS Ano
            FROM PRO_PROCESSO_VALENCA T01
            INNER JOIN DAR_DOMINIO_ATRIBUTO_VALENCA T02 
                ON T01.TIP_ORIGEM_PROCESSO = T02.VAL_ATRIBUTO
               AND T02.NOM_ATRIBUTO = 'TIP_ORIGEM_PROCESSO'
            LEFT JOIN INS_INSTANCIA_VALENCA T03 
                ON T01.ISN_PROCESSO = T03.ISN_PROCESSO
            WHERE TRY_CONVERT(date, T03.DAT_INSTANCIA) IS NOT NULL
              AND T02.DES_ATRIBUTO = 'Importação'
              AND YEAR(TRY_CONVERT(date, T03.DAT_INSTANCIA)) = {filters.year}
        ),
        Meses AS (
            SELECT 7 AS Mes
            UNION ALL SELECT 8
            UNION ALL SELECT 9
            UNION ALL SELECT 10
            UNION ALL SELECT 11
            UNION ALL SELECT 12
        )
        SELECT 
            M.Mes,
            DATENAME(MONTH, DATEFROMPARTS({filters.year}, M.Mes, 1)) AS NomeMes,
            ISNULL(C.Total, 0) AS TotalImportacao
        FROM Meses M
        LEFT JOIN (
            SELECT Mes, COUNT(*) AS Total
            FROM Base
            GROUP BY Mes
        ) C ON M.Mes = C.Mes
        ORDER BY M.Mes
    """
    return run_query(sql)