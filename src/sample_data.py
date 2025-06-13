from datetime import date, time

def get_sample_data(template_type: str | None = None):
    """Restituisce un dizionario con dati di esempio utili a popolare i template in fase di test.
    Il parametro template_type serve ad aggiungere campi specifici per alcuni template.
    """
    base = {
        'denominazione': 'ACME S.r.l.',
        'sede_legale': 'Via Roma 1, Milano (MI)',
        'capitale_sociale': '10.000,00',
        'codice_fiscale': '12345678901',
        'data_assemblea': date.today(),
        'ora_inizio': time(9, 0),
        'ora_chiusura': time(10, 0),
        'presidente': 'Mario Rossi',
        'segretario': 'Luigi Bianchi',
        'soci': [
            {
                'nome': 'Mario Rossi',
                'tipo_soggetto': 'Persona Fisica',
                'tipo_partecipazione': 'Diretto',
                'quota_euro': '5.000,00',
                'quota_percentuale': '50',
                'presente': True,
                'delegato': '',
                'rappresentante_legale': ''
            },
            {
                'nome': 'Tech Holdings S.p.A.',
                'tipo_soggetto': 'Società',
                'tipo_partecipazione': 'Diretto',
                'quota_euro': '5.000,00',
                'quota_percentuale': '50',
                'presente': True,
                'delegato': '',
                'rappresentante_legale': 'Anna Verdi'
            }
        ],
        'amministratori': [
            {'nome': 'Mario Rossi', 'carica': 'Amministratore Unico', 'presente': True},
            {'nome': 'Luigi Bianchi', 'carica': 'Consigliere', 'presente': True}
        ]
    }

    # Aggiunte specifiche per determinati template
    if template_type == 'verbale_assemblea_consiglio_amministrazione':
        base.update({
            'motivo_nomina': 'Dimissioni dell\'organo in carica',
            'consiglieri': [
                {
                    'nome': 'Mario Rossi',
                    'data_nascita': date(1980, 1, 1),
                    'luogo_nascita': 'Milano',
                    'codice_fiscale': 'RSSMRA80A01F205X',
                    'residenza': 'Milano',
                    'qualifica': 'Socio'
                },
                {
                    'nome': 'Luigi Bianchi',
                    'data_nascita': date(1982, 5, 10),
                    'luogo_nascita': 'Roma',
                    'codice_fiscale': 'BNCLGU82E10H501Y',
                    'residenza': 'Roma',
                    'qualifica': 'Socio'
                },
                {
                    'nome': 'Carla Verdi',
                    'data_nascita': date(1979, 3, 20),
                    'luogo_nascita': 'Torino',
                    'codice_fiscale': 'VRDCLL79C60L219Z',
                    'residenza': 'Torino',
                    'qualifica': 'Socio'
                }
            ],
            'presidente_cda_option': 'Nomina diretta in assemblea',
            'presidente_cda': 'Mario Rossi',
            'include_compensi': True,
            'compenso_annuo': '0,00',
            'rimborso_spese': True,
            'durata_incarico': 'A tempo indeterminato fino a revoca o dimissioni'
        })

    elif template_type == 'verbale_assemblea_amministratore_unico_template':
        base.update({
            'motivo_nomina': 'Prima nomina',
            'tipo_assemblea': 'regolarmente convocata',
            'amministratore_unico': {
                'nome': 'Mario Rossi',
                'data_nascita': date(1980, 1, 1),
                'luogo_nascita': 'Milano',
                'codice_fiscale': 'RSSMRA80A01F205X',
                'residenza': 'Milano',
                'qualifica': 'Socio'
            }
        })

    # Può essere esteso con altri template

    return base 