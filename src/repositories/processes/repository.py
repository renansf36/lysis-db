from datetime import date
from typing import Optional, Tuple

from src.infra.db import run_query
from src.schemas.schemas import (
    DateRangeFilter,
    OriginDateFilter,
    YearFilter,
)


def _serialize_date(value: Optional[date]) -> Optional[str]:
    return value.isoformat() if value else None


def _date_filter_params(filters: DateRangeFilter) -> Tuple[
    Optional[str],
    Optional[str],
    Optional[str],
    Optional[str],
    Optional[str],
    Optional[str],
]:
    start = _serialize_date(filters.start_date)
    end = _serialize_date(filters.end_date)
    return (start, end, start, start, end, end)


def _instance_date_expr(table_alias: str) -> str:
    return (
        f"TRY_CONVERT(date, NULLIF(LTRIM(RTRIM({table_alias}.DAT_INSTANCIA)), ''))"
    )


def _date_filter_clause(date_expr: str) -> str:
    return f"""
        WHERE (
            (%s IS NULL AND %s IS NULL)
            OR {date_expr} IS NOT NULL
        )
          AND (%s IS NULL OR {date_expr} >= %s)
          AND (%s IS NULL OR {date_expr} <= %s)
    """


def _fetch_origin_last_six_months(
    origin_name: str,
    total_alias: str,
    filters: DateRangeFilter,
):
    start = _serialize_date(filters.start_date)
    end = _serialize_date(filters.end_date)
    start_month = filters.start_date.replace(day=1).isoformat()
    end_month = filters.end_date.replace(day=1).isoformat()
    sql = f"""
        WITH Base AS (
            SELECT DATEFROMPARTS(
                       YEAR(TRY_CONVERT(date, T01.DAT_STATUS)),
                       MONTH(TRY_CONVERT(date, T01.DAT_STATUS)),
                       1
                   ) AS MesRef
            FROM PRO_PROCESSO_VALENCA T01
            INNER JOIN DAR_DOMINIO_ATRIBUTO_VALENCA T02
                ON T01.TIP_ORIGEM_PROCESSO = T02.VAL_ATRIBUTO
               AND T02.NOM_ATRIBUTO = 'TIP_ORIGEM_PROCESSO'
            WHERE TRY_CONVERT(date, T01.DAT_STATUS) IS NOT NULL
              AND T02.DES_ATRIBUTO = %s
              AND TRY_CONVERT(date, T01.DAT_STATUS) >= %s
              AND TRY_CONVERT(date, T01.DAT_STATUS) < DATEADD(day, 1, %s)
        ),
        Meses AS (
            SELECT TRY_CONVERT(date, %s) AS MesRef
            UNION ALL
            SELECT DATEADD(month, 1, MesRef)
            FROM Meses
            WHERE DATEADD(month, 1, MesRef) <= TRY_CONVERT(date, %s)
        )
        SELECT
            MONTH(M.MesRef) AS Mes,
            DATENAME(MONTH, M.MesRef) AS NomeMes,
            ISNULL(C.Total, 0) AS {total_alias}
        FROM Meses M
        LEFT JOIN (
            SELECT MesRef, COUNT(*) AS Total
            FROM Base
            GROUP BY MesRef
        ) C ON M.MesRef = C.MesRef
        ORDER BY M.MesRef
        OPTION (MAXRECURSION 1000)
    """
    return run_query(sql, (origin_name, start, end, start_month, end_month))


def fetch_process_count():
    sql = """
        SELECT COUNT(*) AS total_processos
        FROM PRO_PROCESSO_VALENCA
    """
    return run_query(sql)


def fetch_by_origin(filters: DateRangeFilter):
    instance_date = _instance_date_expr("T03")
    sql = f"""
        SELECT COUNT(*) AS total,
               T02.DES_ATRIBUTO AS origin
        FROM PRO_PROCESSO_VALENCA T01
        INNER JOIN DAR_DOMINIO_ATRIBUTO_VALENCA T02
            ON T01.TIP_ORIGEM_PROCESSO = T02.VAL_ATRIBUTO
           AND T02.NOM_ATRIBUTO = 'TIP_ORIGEM_PROCESSO'
        LEFT JOIN INS_INSTANCIA_VALENCA T03
            ON T01.ISN_PROCESSO = T03.ISN_PROCESSO
        {_date_filter_clause(instance_date)}
        GROUP BY T02.DES_ATRIBUTO
        ORDER BY total DESC
    """
    return run_query(sql, _date_filter_params(filters))


def fetch_by_status(filters: DateRangeFilter):
    instance_date = _instance_date_expr("T03")
    sql = f"""
        SELECT COUNT(*) AS total,
               T02.DES_ATRIBUTO AS status
        FROM PRO_PROCESSO_VALENCA T01
        INNER JOIN DAR_DOMINIO_ATRIBUTO_VALENCA T02
            ON T01.STA_PROCESSO = T02.VAL_ATRIBUTO
           AND T02.NOM_ATRIBUTO = 'STA_PROCESSO'
        LEFT JOIN INS_INSTANCIA_VALENCA T03
            ON T01.ISN_PROCESSO = T03.ISN_PROCESSO
        {_date_filter_clause(instance_date)}
        GROUP BY T02.DES_ATRIBUTO
        ORDER BY T02.DES_ATRIBUTO
    """
    return run_query(sql, _date_filter_params(filters))


def fetch_by_matter(filters: DateRangeFilter):
    instance_date = _instance_date_expr("T03")
    sql = f"""
        SELECT COUNT(*) AS total,
               COALESCE(T02.NOM_MATERIA, 'Não informado') AS subject
        FROM PRO_PROCESSO_VALENCA T01
        LEFT JOIN MAT_MATERIA_VALENCA T02
            ON T01.ISN_MATERIA = T02.ISN_MATERIA
        LEFT JOIN INS_INSTANCIA_VALENCA T03
            ON T01.ISN_PROCESSO = T03.ISN_PROCESSO
        {_date_filter_clause(instance_date)}
        GROUP BY COALESCE(T02.NOM_MATERIA, 'Não informado')
        ORDER BY subject
    """
    return run_query(sql, _date_filter_params(filters))


def fetch_by_group(filters: DateRangeFilter):
    instance_date = _instance_date_expr("T03")
    sql = f"""
        SELECT COUNT(*) AS total,
               COALESCE(T02.DSC_GRUPO_PROCESSO, 'Não informado') AS process_group
        FROM PRO_PROCESSO_VALENCA T01
        LEFT JOIN GPP_GRUPO_PROCESSO_VALENCA T02
            ON T01.ISN_GRUPO_PROCESSO = T02.ISN_GRUPO_PROCESSO
        LEFT JOIN INS_INSTANCIA_VALENCA T03
            ON T01.ISN_PROCESSO = T03.ISN_PROCESSO
        {_date_filter_clause(instance_date)}
        GROUP BY COALESCE(T02.DSC_GRUPO_PROCESSO, 'Não informado')
        ORDER BY process_group
    """
    return run_query(sql, _date_filter_params(filters))


def fetch_by_organization(filters: DateRangeFilter):
    instance_date = _instance_date_expr("T02")
    sql = f"""
        SELECT COUNT(*) AS total,
               COALESCE(T03.DSC_ORGAO, 'Não informado') AS agency
        FROM PRO_PROCESSO_VALENCA T01
        LEFT JOIN INS_INSTANCIA_VALENCA T02
            ON T01.ISN_PROCESSO = T02.ISN_PROCESSO
        LEFT JOIN ORG_ORGAO_VALENCA T03
            ON T02.ISN_ORGAO = T03.ISN_ORGAO
        {_date_filter_clause(instance_date)}
        GROUP BY COALESCE(T03.DSC_ORGAO, 'Não informado')
        ORDER BY agency
    """
    return run_query(sql, _date_filter_params(filters))


def fetch_by_origin_with_instance_date_filter(filters: OriginDateFilter):
    instance_date = _instance_date_expr("T03")
    sql = f"""
        SELECT COUNT(1) AS Quantidade,
               T02.DES_ATRIBUTO AS Origem
        FROM PRO_PROCESSO_VALENCA T01
        INNER JOIN DAR_DOMINIO_ATRIBUTO_VALENCA T02
            ON T01.TIP_ORIGEM_PROCESSO = T02.VAL_ATRIBUTO
           AND T02.NOM_ATRIBUTO = 'TIP_ORIGEM_PROCESSO'
        LEFT JOIN INS_INSTANCIA_VALENCA T03
            ON T01.ISN_PROCESSO = T03.ISN_PROCESSO
        WHERE {instance_date} IS NOT NULL
          AND {instance_date} >= %s
          AND {instance_date} <= %s
        GROUP BY T02.DES_ATRIBUTO
        ORDER BY T02.DES_ATRIBUTO
    """
    params = (
        _serialize_date(filters.start_date),
        _serialize_date(filters.end_date),
    )
    return run_query(sql, params)


def fetch_by_origin_registration_by_year_range(filters: DateRangeFilter):
    sql = """
        SELECT YEAR(p.DAT_CADASTRO) AS Ano,
               COUNT(DISTINCT i.NUM_PROCESSO) AS TotalCadastro
        FROM PRO_PROCESSO_VALENCA p
        LEFT JOIN INS_INSTANCIA_VALENCA i
            ON i.ISN_PROCESSO = p.ISN_PROCESSO
        INNER JOIN DAR_DOMINIO_ATRIBUTO_VALENCA T02
           ON p.TIP_ORIGEM_PROCESSO = T02.VAL_ATRIBUTO
           AND T02.NOM_ATRIBUTO = 'TIP_ORIGEM_PROCESSO'
        WHERE p.DAT_CADASTRO >= %s
          AND p.DAT_CADASTRO < DATEADD(day, 1, %s)
          AND i.NUM_PROCESSO IS NOT NULL
          AND T02.DES_ATRIBUTO = 'Cadastro'
        GROUP BY YEAR(p.DAT_CADASTRO)
        ORDER BY Ano
    """
    params = (
        _serialize_date(filters.start_date),
        _serialize_date(filters.end_date),
    )
    return run_query(sql, params)


def fetch_process_registration_details_by_year_range(filters: DateRangeFilter):
    sql = """
        SELECT YEAR(p.DAT_CADASTRO) AS Ano,
               COUNT(DISTINCT iiv.NUM_PROCESSO) AS TotalCadastro,
               ddav.DES_ATRIBUTO AS OrigemProcesso,
               ddav02.DES_ATRIBUTO AS StatusProcesso,
               COALESCE(mmv.NOM_MATERIA, 'Não informado') AS materia,
               COALESCE(ggpv.DSC_GRUPO_PROCESSO, 'Não informado') AS equipe,
               COALESCE(oov.DSC_ORGAO, 'Não informado') AS orgao
        FROM PRO_PROCESSO_VALENCA p
        LEFT JOIN INS_INSTANCIA_VALENCA iiv
            ON iiv.ISN_PROCESSO = p.ISN_PROCESSO
        INNER JOIN DAR_DOMINIO_ATRIBUTO_VALENCA ddav
            ON p.TIP_ORIGEM_PROCESSO = ddav.VAL_ATRIBUTO
           AND ddav.NOM_ATRIBUTO = 'TIP_ORIGEM_PROCESSO'
        INNER JOIN DAR_DOMINIO_ATRIBUTO_VALENCA ddav02
            ON p.STA_PROCESSO = ddav02.VAL_ATRIBUTO
           AND ddav02.NOM_ATRIBUTO = 'STA_PROCESSO'
        LEFT JOIN MAT_MATERIA_VALENCA mmv
            ON p.ISN_MATERIA = mmv.ISN_MATERIA
        LEFT JOIN GPP_GRUPO_PROCESSO_VALENCA ggpv
            ON p.ISN_GRUPO_PROCESSO = ggpv.ISN_GRUPO_PROCESSO
        LEFT JOIN ORG_ORGAO_VALENCA oov
            ON iiv.ISN_ORGAO = oov.ISN_ORGAO
        WHERE p.DAT_CADASTRO >= %s
          AND p.DAT_CADASTRO < DATEADD(day, 1, %s)
          AND iiv.NUM_PROCESSO IS NOT NULL
          AND ddav.DES_ATRIBUTO = 'Cadastro'
        GROUP BY YEAR(p.DAT_CADASTRO),
                 ddav.DES_ATRIBUTO,
                 ddav02.DES_ATRIBUTO,
                 mmv.NOM_MATERIA,
                 ggpv.DSC_GRUPO_PROCESSO,
                 oov.DSC_ORGAO
        ORDER BY Ano
    """
    params = (
        _serialize_date(filters.start_date),
        _serialize_date(filters.end_date),
    )
    return run_query(sql, params)


def fetch_by_origin_registration_last_six_months(filters: DateRangeFilter):
    return _fetch_origin_last_six_months(
        origin_name="Cadastro",
        total_alias="TotalCadastro",
        filters=filters,
    )


def fetch_by_origin_capture_last_six_months(filters: DateRangeFilter):
    return _fetch_origin_last_six_months(
        origin_name="Captura",
        total_alias="TotalCaptura",
        filters=filters,
    )


def fetch_by_origin_distribution_last_six_months(filters: DateRangeFilter):
    return _fetch_origin_last_six_months(
        origin_name="Distribuição",
        total_alias="TotalDistribuicao",
        filters=filters,
    )


def fetch_by_origin_import_last_six_months(filters: YearFilter):
    return _fetch_origin_last_six_months(
        origin_name="Importação",
        total_alias="TotalImportacao",
        year=filters.year,
    )


def fetch_by_origin_with_date_range(filters: DateRangeFilter):
    instance_date = _instance_date_expr("T03")
    sql = f"""
        SELECT COUNT(1) AS Quantidade,
               T02.DES_ATRIBUTO AS Origem
        FROM PRO_PROCESSO_VALENCA T01
        INNER JOIN DAR_DOMINIO_ATRIBUTO_VALENCA T02
            ON T01.TIP_ORIGEM_PROCESSO = T02.VAL_ATRIBUTO
           AND T02.NOM_ATRIBUTO = 'TIP_ORIGEM_PROCESSO'
        LEFT JOIN INS_INSTANCIA_VALENCA T03
            ON T01.ISN_PROCESSO = T03.ISN_PROCESSO
        WHERE {instance_date} IS NOT NULL
          AND {instance_date} >= %s
          AND {instance_date} <= %s
        GROUP BY T02.DES_ATRIBUTO
        ORDER BY T02.DES_ATRIBUTO
    """
    params = (
        _serialize_date(filters.start_date),
        _serialize_date(filters.end_date),
    )
    return run_query(sql, params)


def fetch_by_origin_with_date_range_detailed(filters: DateRangeFilter):
    instance_date = _instance_date_expr("T03")
    sql = f"""
        SELECT T02.DES_ATRIBUTO AS Origem,
               YEAR({instance_date}) AS Ano,
               MONTH({instance_date}) AS Mes,
               COUNT(1) AS Quantidade
        FROM PRO_PROCESSO_VALENCA T01
        INNER JOIN DAR_DOMINIO_ATRIBUTO_VALENCA T02
            ON T01.TIP_ORIGEM_PROCESSO = T02.VAL_ATRIBUTO
           AND T02.NOM_ATRIBUTO = 'TIP_ORIGEM_PROCESSO'
        LEFT JOIN INS_INSTANCIA_VALENCA T03
            ON T01.ISN_PROCESSO = T03.ISN_PROCESSO
        WHERE {instance_date} IS NOT NULL
          AND {instance_date} >= %s
          AND {instance_date} <= %s
        GROUP BY T02.DES_ATRIBUTO,
                 YEAR({instance_date}),
                 MONTH({instance_date})
        ORDER BY Ano,
                 Mes,
                 Origem
    """
    params = (
        _serialize_date(filters.start_date),
        _serialize_date(filters.end_date),
    )
    return run_query(sql, params)


def fetch_publication_by_matter_year(filters: YearFilter):
    sql = """
        SELECT COUNT(*) AS total,
               COALESCE(TMAT.NOM_MATERIA, 'Não informado') AS subject
        FROM ADA_ANDAMENTO_VALENCA T01
        INNER JOIN PRO_PROCESSO_VALENCA TPROC
            ON T01.ISN_PROCESSO = TPROC.ISN_PROCESSO
        LEFT JOIN MAT_MATERIA_VALENCA TMAT
            ON TPROC.ISN_MATERIA = TMAT.ISN_MATERIA
        WHERE T01.TIP_ORIGEM = 3
          AND T01.DAT_EXCLUSAO IS NULL
          AND T01.DAT_EXCLUSAO_CADASTRO IS NULL
          AND YEAR(T01.DAT_INCLUSAO) = %s
        GROUP BY COALESCE(TMAT.NOM_MATERIA, 'Não informado')
        ORDER BY subject
    """
    return run_query(sql, (filters.year,))


def fetch_publication_by_matter_total():
    sql = """
        SELECT COUNT(*) AS total,
               COALESCE(TMAT.NOM_MATERIA, 'Não informado') AS subject
        FROM ADA_ANDAMENTO_VALENCA T01
        INNER JOIN PRO_PROCESSO_VALENCA TPROC
            ON T01.ISN_PROCESSO = TPROC.ISN_PROCESSO
        LEFT JOIN MAT_MATERIA_VALENCA TMAT
            ON TPROC.ISN_MATERIA = TMAT.ISN_MATERIA
        WHERE T01.TIP_ORIGEM = 3
          AND T01.DAT_EXCLUSAO IS NULL
          AND T01.DAT_EXCLUSAO_CADASTRO IS NULL
        GROUP BY COALESCE(TMAT.NOM_MATERIA, 'Não informado')
        ORDER BY subject
    """
    return run_query(sql)


def fetch_publication_by_matter_last_six_months(filters: YearFilter):
    sql = """
        WITH Base AS (
            SELECT MONTH(TRY_CONVERT(date, T01.DAT_INCLUSAO)) AS Mes
            FROM ADA_ANDAMENTO_VALENCA T01
            WHERE T01.TIP_ORIGEM = 3
              AND T01.DAT_EXCLUSAO IS NULL
              AND T01.DAT_EXCLUSAO_CADASTRO IS NULL
              AND TRY_CONVERT(date, T01.DAT_INCLUSAO) IS NOT NULL
              AND YEAR(TRY_CONVERT(date, T01.DAT_INCLUSAO)) = %s
        ),
        Meses AS (
            SELECT 7 AS Mes
            UNION ALL SELECT 8
            UNION ALL SELECT 9
            UNION ALL SELECT 10
            UNION ALL SELECT 11
            UNION ALL SELECT 12
        )
        SELECT M.Mes,
               DATENAME(MONTH, DATEFROMPARTS(%s, M.Mes, 1)) AS NomeMes,
               ISNULL(C.Total, 0) AS TotalPublicacoes
        FROM Meses M
        LEFT JOIN (
            SELECT Mes, COUNT(*) AS Total
            FROM Base
            GROUP BY Mes
        ) C ON M.Mes = C.Mes
        ORDER BY M.Mes
    """
    return run_query(sql, (filters.year, filters.year))


def fetch_publication_by_matter_last_month(filters: YearFilter):
    sql = """
        WITH Base AS (
            SELECT TRY_CONVERT(date, T01.DAT_INCLUSAO) AS DataPublicacao,
                   MONTH(TRY_CONVERT(date, T01.DAT_INCLUSAO)) AS Mes,
                   YEAR(TRY_CONVERT(date, T01.DAT_INCLUSAO)) AS Ano,
                   T01.ISN_PROCESSO
            FROM ADA_ANDAMENTO_VALENCA T01
            WHERE T01.TIP_ORIGEM = 3
              AND T01.DAT_EXCLUSAO IS NULL
              AND T01.DAT_EXCLUSAO_CADASTRO IS NULL
              AND TRY_CONVERT(date, T01.DAT_INCLUSAO) IS NOT NULL
              AND YEAR(TRY_CONVERT(date, T01.DAT_INCLUSAO)) = %s
        ),
        UltimoMes AS (
            SELECT MAX(Ano) AS Ano,
                   MAX(Mes) AS Mes
            FROM Base
        )
        SELECT COUNT(*) AS total,
               COALESCE(TMAT.NOM_MATERIA, 'Não informado') AS subject
        FROM Base B
        INNER JOIN UltimoMes U
            ON B.Ano = U.Ano
           AND B.Mes = U.Mes
        INNER JOIN PRO_PROCESSO_VALENCA TPROC
            ON B.ISN_PROCESSO = TPROC.ISN_PROCESSO
        LEFT JOIN MAT_MATERIA_VALENCA TMAT
            ON TPROC.ISN_MATERIA = TMAT.ISN_MATERIA
        GROUP BY COALESCE(TMAT.NOM_MATERIA, 'Não informado')
        ORDER BY subject
    """
    return run_query(sql, (filters.year,))


def fetch_process_inclusion_report(
    filters: DateRangeFilter,
    limit: int,
    offset: int,
):
    base_ctes = """
        WITH ProcessosBase AS (
            SELECT
                p.ISN_PROCESSO,
                i.NUM_PROCESSO,
                MIN(a.DAT_INCLUSAO) AS DAT_INCLUSAO_PROCESSO
            FROM PRO_PROCESSO_VALENCA p
            INNER JOIN INS_INSTANCIA_VALENCA i
                ON i.ISN_PROCESSO = p.ISN_PROCESSO
            INNER JOIN ADA_ANDAMENTO_VALENCA a
                ON a.ISN_PROCESSO = p.ISN_PROCESSO
            WHERE p.STA_PROCESSO = 0
              AND a.DAT_INCLUSAO >= %s
              AND a.DAT_INCLUSAO < DATEADD(day, 1, %s)
            GROUP BY
                p.ISN_PROCESSO,
                i.NUM_PROCESSO
        ),
        InstanciaPrincipal AS (
            SELECT
                i.*,
                ROW_NUMBER() OVER (
                    PARTITION BY i.ISN_PROCESSO
                    ORDER BY i.DAT_INSTANCIA DESC, i.ISN_INSTANCIA DESC
                ) AS RN
            FROM INS_INSTANCIA_VALENCA i
            INNER JOIN ProcessosBase pb
                ON pb.ISN_PROCESSO = i.ISN_PROCESSO
        ),
        Partes AS (
            SELECT
                par.ISN_PROCESSO,
                pes.NOM_PESSOA,
                tpp.DSC_TIPO_PARTE,
                CASE
                    WHEN UPPER(tpp.DSC_TIPO_PARTE) IN (
                        'AUTOR', 'RECLAMANTE', 'EXEQUENTE', 'REQUERENTE',
                        'POLO ATIVO', 'ATIVO', 'DEMANDANTE', 'AGRAVANTE',
                        'EMBARGANTE', 'APELANTE'
                    ) THEN 'ATIVO'
                    WHEN UPPER(tpp.DSC_TIPO_PARTE) IN (
                        'REU', 'RECLAMADO', 'RECLAMADO(A)', 'EXECUTADO',
                        'REQUERIDO', 'POLO PASSIVO', 'PASSIVO', 'DEMANDADO',
                        'AGRAVADO', 'EMBARGADO', 'APELADO', 'PARTE RE',
                        'LITISCONSORTE PASSIVO'
                    ) THEN 'PASSIVO'
                    ELSE 'OUTROS'
                END AS TIPO_POLO
            FROM PAR_PARTE_VALENCA par
            INNER JOIN PES_PESSOA_VALENCA pes
                ON pes.ISN_PESSOA = par.ISN_PESSOA
            INNER JOIN TPA_TIPO_PARTE_VALENCA tpp
                ON tpp.ISN_TIPO_PARTE = par.ISN_TIPO_PARTE
            INNER JOIN ProcessosBase pb
                ON pb.ISN_PROCESSO = par.ISN_PROCESSO
        ),
        PartesPivot AS (
            SELECT
                ISN_PROCESSO,
                MAX(CASE WHEN TIPO_POLO = 'ATIVO' THEN NOM_PESSOA END)
                    AS PARTE_POLO_ATIVO,
                MAX(CASE WHEN TIPO_POLO = 'PASSIVO' THEN NOM_PESSOA END)
                    AS PARTE_POLO_PASSIVO,
                MAX(CASE WHEN TIPO_POLO = 'ATIVO' THEN DSC_TIPO_PARTE END)
                    AS TIPO_PARTE_ATIVO,
                MAX(CASE WHEN TIPO_POLO = 'PASSIVO' THEN DSC_TIPO_PARTE END)
                    AS TIPO_PARTE_PASSIVO
            FROM Partes
            GROUP BY ISN_PROCESSO
        )
    """

    count_sql = base_ctes + """
        SELECT COUNT(*) AS total
        FROM ProcessosBase
    """

    data_sql = base_ctes + """
        , Relatorio AS (
            SELECT
                CONVERT(date, pb.DAT_INCLUSAO_PROCESSO)
                    AS [Data de Inclusao do Processo],
                CONVERT(date, p.DAT_VLR_PROVISIONADO)
                    AS [Data da Contratacao],
                CONVERT(date, p.DAT_DISTRIBUICAO)
                    AS [Data da Distribuicao],
                pb.NUM_PROCESSO AS [N Processo],
                p.NOM_PROCESSO AS [Titulo],
                pp.TIPO_PARTE_PASSIVO + ': ' + pp.PARTE_POLO_PASSIVO
                    AS [Parte Cliente],
                pp.TIPO_PARTE_ATIVO + ': ' + pp.PARTE_POLO_ATIVO
                    AS [Parte Contraria],
                pp.TIPO_PARTE_PASSIVO AS [Tipo de Parte do Cliente],
                pp.PARTE_POLO_ATIVO AS [Parte Polo Ativo Principal],
                pp.PARTE_POLO_PASSIVO AS [Parte Polo Passivo Principal],
                aca.DSC_ACAO AS [Tipo de Acao],
                ip.ISN_INSTANCIA AS [N Unidade],
                g.DSC_GRUPO_PROCESSO AS [Unidade],
                mmv.NOM_MATERIA AS [Especialidade],
                org.DSC_ORGAO AS [Orgao],
                CONVERT(varchar(10), ip.DAT_INSTANCIA, 103)
                    + ' - '
                    + COALESCE(ti.DSC_TIPO_INSTANCIA, 'Instancia')
                    + ' - '
                    + ip.NUM_PROCESSO
                    + ' '
                    + COALESCE(ip.NUM_PROCESSO_ANTERIOR, 'N/A')
                    + ' '
                    + COALESCE(vr.DSC_VARA, '')
                    + ' - '
                    + COALESCE(coma.DSC_COMARCA, '')
                    + ' - '
                    + COALESCE(est.NOM_ESTADO, '') AS [Instancias],
                coma.DSC_COMARCA AS [Comarca],
                est.NOM_ESTADO AS [Estado],
                se.DSC_SISTEMA_EXTERNO AS [Sistema Externo],
                CASE
                    WHEN p.TIP_ELETRONICO = 1 THEN 'SIM'
                    ELSE 'NAO'
                END AS [Processo Eletronico],
                mmv.NOM_MATERIA AS [Materia],
                nat.DSC_NATUREZA AS [Natureza],
                rit.DSC_RITO AS [Rito],
                p.VLR_CAUSA AS [Valor da Causa],
                CAST(p.DSC_OBJETO AS NVARCHAR(MAX)) AS [Objetos],
                CAST(p.DSC_OBJETO AS NVARCHAR(MAX)) AS [Descricao do Objeto],
                dd_status.DES_ATRIBUTO AS [Status],
                fas.DSC_FASE AS [Fase],
                g.DSC_GRUPO_PROCESSO AS [Grupo de Processo],
                pri.NOM_PESSOA AS [Prioridade de],
                gp.NOM_GRUPO_PESSOA AS [Grupo de Pessoa],
                cli.NUM_CNPJ AS [N CNPJ da Parte Cliente],
                cli.NOM_PESSOA AS [Cliente],
                p.VLR_FINAL_CAUSA AS [Valor Final da Causa],
                p.ISN_PROCESSO AS [Identificador do Processo],
                CASE
                    WHEN p.TIP_ESTRATEGICO = 1 THEN 'SIM'
                    ELSE 'NAO'
                END AS [Processo Estrategico],
                p.ISN_PROCESSO_PAI AS [Apensos],
                NULL AS [Data da Garantia],
                NULL AS [Valor da Garantia],
                NULL AS [Tipo de Garantia],
                prp.DSC_PROBABILIDADE_PERDA AS [Probabilidade de Perda],
                CAST(p.DSC_PARECER AS NVARCHAR(MAX)) AS [Parecer],
                emp.NOM_PESSOA AS [Responsavel Inclusao do Processo],
                dd_origem.DES_ATRIBUTO AS [Origem do Processo],
                tre.DSC_TIPO_RESULTADO AS [Tipo de Resultado],
                CAST(p.DSC_RESULTADO AS NVARCHAR(MAX))
                    AS [Descricao do Resultado],
                CAST(p.DSC_OBSERVACAO_001 AS NVARCHAR(MAX)) AS [Observacao]
            FROM ProcessosBase pb
            INNER JOIN PRO_PROCESSO_VALENCA p
                ON p.ISN_PROCESSO = pb.ISN_PROCESSO
            LEFT JOIN InstanciaPrincipal ip
                ON ip.ISN_PROCESSO = p.ISN_PROCESSO
               AND ip.RN = 1
            LEFT JOIN PartesPivot pp
                ON pp.ISN_PROCESSO = p.ISN_PROCESSO
            LEFT JOIN PES_PESSOA_VALENCA cli
                ON cli.ISN_PESSOA = p.ISN_PESSOA_CLIENTE
            LEFT JOIN PES_PESSOA_VALENCA pri
                ON pri.ISN_PESSOA = p.ISN_PESSOA_PRIORIDADE
            LEFT JOIN PES_PESSOA_VALENCA emp
                ON emp.ISN_PESSOA = p.ISN_EMPRESA
            LEFT JOIN MAT_MATERIA_VALENCA mmv
                ON mmv.ISN_MATERIA = p.ISN_MATERIA
            LEFT JOIN GPP_GRUPO_PROCESSO_VALENCA g
                ON g.ISN_GRUPO_PROCESSO = p.ISN_GRUPO_PROCESSO
               AND g.ISN_EMPRESA = p.ISN_EMPRESA
            LEFT JOIN ACA_ACAO_VALENCA aca
                ON aca.ISN_ACAO = p.ISN_ACAO
               AND aca.ISN_EMPRESA = p.ISN_EMPRESA
            LEFT JOIN FAS_FASE_VALENCA fas
                ON fas.ISN_FASE = p.ISN_FASE
               AND fas.ISN_EMPRESA = p.ISN_EMPRESA
            LEFT JOIN NAT_NATUREZA_VALENCA nat
                ON nat.ISN_NATUREZA = p.ISN_NATUREZA
               AND nat.ISN_EMPRESA = p.ISN_EMPRESA
            LEFT JOIN RIT_RITO_VALENCA rit
                ON rit.ISN_RITO = p.ISN_RITO
               AND rit.ISN_EMPRESA = p.ISN_EMPRESA
            LEFT JOIN DAR_DOMINIO_ATRIBUTO_VALENCA dd_status
                ON dd_status.NOM_ATRIBUTO = 'STA_PROCESSO'
               AND dd_status.VAL_ATRIBUTO = p.STA_PROCESSO
            LEFT JOIN DAR_DOMINIO_ATRIBUTO_VALENCA dd_origem
                ON dd_origem.NOM_ATRIBUTO = 'TIP_ORIGEM_PROCESSO'
               AND dd_origem.VAL_ATRIBUTO = p.TIP_ORIGEM_PROCESSO
            LEFT JOIN PRP_PROBABILIDADE_PERDA_VALENCA prp
                ON prp.ISN_PROBABILIDADE_PERDA = p.ISN_PROBABILIDADE_PERDA
            LEFT JOIN TRE_TIPO_RESULTADO_VALENCA tre
                ON tre.ISN_TIPO_RESULTADO = p.ISN_TIPO_RESULTADO
            LEFT JOIN GPE_GRUPO_PESSOA_VALENCA gp
                ON gp.ISN_GRUPO_PESSOA = cli.ISN_GRUPO_PESSOA
            LEFT JOIN ORG_ORGAO_VALENCA org
                ON org.ISN_ORGAO = ip.ISN_ORGAO
            LEFT JOIN COM_COMARCA_VALENCA coma
                ON coma.ISN_COMARCA = ip.ISN_COMARCA
            LEFT JOIN EST_ESTADO_VALENCA est
                ON est.ISN_ESTADO = coma.ISN_ESTADO
            LEFT JOIN TIN_TIPO_INSTANCIA_VALENCA ti
                ON ti.ISN_TIPO_INSTANCIA = ip.ISN_TIPO_INSTANCIA
            LEFT JOIN VCT_VARA_VALENCA vr
                ON vr.ISN_VARA = ip.ISN_VARA
            LEFT JOIN SIE_SISTEMA_EXTERNO_VALENCA se
                ON se.ISN_SISTEMA_EXTERNO = ip.ISN_SISTEMA_EXTERNO
        )
        SELECT
            *
        FROM Relatorio
        ORDER BY
            [Data de Inclusao do Processo],
            [N Processo],
            [Identificador do Processo]
        OFFSET %s ROWS FETCH NEXT %s ROWS ONLY
    """
    base_params = (
        _serialize_date(filters.start_date),
        _serialize_date(filters.end_date),
    )
    total_rows = run_query(count_sql, base_params)
    total = total_rows[0]["total"] if total_rows else 0

    if total == 0:
        return total, []

    data_params = (
        *base_params,
        offset,
        limit,
    )
    return total, run_query(data_sql, data_params)
