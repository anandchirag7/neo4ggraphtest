# Auto-generated ontology configuration for datasheet documents
# Feel free to edit/extend by hand.

ONTOLOGY_CONFIG = {'7m': {'ics': [{'name': '7M',
                 'pins': ['F0', 'CL', 'C0', 'DL', 'ESR'],
                 'constraints': [{'id': '7M_F0_RANGE',
                                  'pin': '',
                                  'type': 'frequency_range',
                                  'value': None,
                                  'unit': None,
                                  'description': 'Operational frequency range '
                                                 'from 10\u202fMHz to 114\u202f'
                                                 'MHz.',
                                  'keywords': ['10MHz ~ 114MHz',
                                               'Frequency range']},
                                 {'id': '7M_ESR_MAX_10_12MHZ',
                                  'pin': '',
                                  'type': 'max_impedance',
                                  'value': 150,
                                  'unit': 'Ω',
                                  'description': 'Maximum ESR for crystals '
                                                 'operating at 10‑12\u202fMHz.',
                                  'keywords': ['10 ~ 12 MHz',
                                               '150Ω Max',
                                               'ESR']},
                                 {'id': '7M_ESR_MAX_12_16MHZ',
                                  'pin': '',
                                  'type': 'max_impedance',
                                  'value': 80,
                                  'unit': 'Ω',
                                  'description': 'Maximum ESR for crystals '
                                                 'operating at 12‑16\u202fMHz.',
                                  'keywords': ['12 ~ 16 MHz',
                                               '80Ω Max',
                                               'ESR']},
                                 {'id': '7M_ESR_MAX_16_20MHZ',
                                  'pin': '',
                                  'type': 'max_impedance',
                                  'value': 60,
                                  'unit': 'Ω',
                                  'description': 'Maximum ESR for crystals '
                                                 'operating at 16‑20\u202fMHz.',
                                  'keywords': ['16 ~ 20 MHz',
                                               '60Ω Max',
                                               'ESR']},
                                 {'id': '7M_ESR_MAX_20_64MHZ',
                                  'pin': '',
                                  'type': 'max_impedance',
                                  'value': 50,
                                  'unit': 'Ω',
                                  'description': 'Maximum ESR for crystals '
                                                 'operating at 20‑64\u202fMHz.',
                                  'keywords': ['20 ~ 64 MHz',
                                               '50Ω Max',
                                               'ESR']},
                                 {'id': '7M_ESR_MAX_80_114MHZ',
                                  'pin': '',
                                  'type': 'max_impedance',
                                  'value': 60,
                                  'unit': 'Ω',
                                  'description': 'Maximum ESR for crystals '
                                                 'operating at 80‑114\u202f'
                                                 'MHz.',
                                  'keywords': ['80 ~ 114 MHz',
                                               '60Ω Max',
                                               'ESR']},
                                 {'id': '7M_AGING_MAX',
                                  'pin': '',
                                  'type': 'aging',
                                  'value': 3,
                                  'unit': 'ppm',
                                  'description': 'Maximum aging after first '
                                                 'year measured at 25\u202f°C '
                                                 '±3\u202f°C.',
                                  'keywords': ['Aging', '±3ppm']},
                                 {'id': '7M_TSTR_RANGE',
                                  'pin': '',
                                  'type': 'storage_temperature_range',
                                  'value': None,
                                  'unit': None,
                                  'description': 'Storage temperature range '
                                                 'from -40\u202f°C to +85\u202f'
                                                 '°C.',
                                  'keywords': ['Storage Temperature Range',
                                               '-40°C ~ +85°C']},
                                 {'id': '7M_DL_RANGE',
                                  'pin': '',
                                  'type': 'drive_level',
                                  'value': None,
                                  'unit': None,
                                  'description': 'Drive level 1\u202fµW to '
                                                 '200\u202fµW (100\u202fµW '
                                                 'typical).',
                                  'keywords': ['Drive Level',
                                               '1 ~ 200μW',
                                               '100μW Typ']},
                                 {'id': '7M_CL_VALUES',
                                  'pin': '',
                                  'type': 'load_capacitance',
                                  'value': None,
                                  'unit': None,
                                  'description': 'Available load capacitance '
                                                 'values: 6, 7, 8, 9, 10, 12, '
                                                 '16, 18, 20\u202fpF.',
                                  'keywords': ['Load Capacitance',
                                               '6pF 7pF 8pF 9pF 10pF 12pF 16pF '
                                               '18pF 20pF']},
                                 {'id': '7M_C0_MAX',
                                  'pin': '',
                                  'type': 'shunt_capacitance',
                                  'value': 3,
                                  'unit': 'pF',
                                  'description': 'Maximum shunt capacitance is '
                                                 '3\u202fpF.',
                                  'keywords': ['Shunt Capacitance', '3pF Max']},
                                 {'id': '7M_TOTR_RANGE',
                                  'pin': '',
                                  'type': 'operating_temperature_range',
                                  'value': None,
                                  'unit': None,
                                  'description': 'Operating temperature range '
                                                 'from -20\u202f°C to +70\u202f'
                                                 '°C.',
                                  'keywords': ['Operating Temperature Range',
                                               '-20°C ~ +70°C']},
                                 {'id': '7M_FSTAB_A',
                                  'pin': '',
                                  'type': 'frequency_stability',
                                  'value': 30,
                                  'unit': 'ppm',
                                  'description': 'Frequency stability ±30\u202f'
                                                 'ppm over -20\u202f°C to '
                                                 '+70\u202f°C for grade A.',
                                  'keywords': ['Frequency Stability',
                                               '±30 ppm',
                                               '-20°C ~ +70°C']},
                                 {'id': '7M_FSTAB_D',
                                  'pin': '',
                                  'type': 'frequency_stability',
                                  'value': 20,
                                  'unit': 'ppm',
                                  'description': 'Frequency stability ±20\u202f'
                                                 'ppm over -20\u202f°C to '
                                                 '+70\u202f°C for grade D.',
                                  'keywords': ['Frequency Stability',
                                               '±20 ppm',
                                               '-20°C ~ +70°C']},
                                 {'id': '7M_FSTAB_E',
                                  'pin': '',
                                  'type': 'frequency_stability',
                                  'value': 10,
                                  'unit': 'ppm',
                                  'description': 'Frequency stability ±10\u202f'
                                                 'ppm over -20\u202f°C to '
                                                 '+70\u202f°C for grade E.',
                                  'keywords': ['Frequency Stability',
                                               '±10 ppm',
                                               '-20°C ~ +70°C']},
                                 {'id': '7M_FSTAB_T',
                                  'pin': '',
                                  'type': 'frequency_stability',
                                  'value': 10,
                                  'unit': 'ppm',
                                  'description': 'Frequency stability ±10\u202f'
                                                 'ppm over -30\u202f°C to '
                                                 '+85\u202f°C for grade T.',
                                  'keywords': ['Frequency Stability',
                                               '±10 ppm',
                                               '-30°C ~ +85°C']},
                                 {'id': '7M_FSTAB_H',
                                  'pin': '',
                                  'type': 'frequency_stability',
                                  'value': 30,
                                  'unit': 'ppm',
                                  'description': 'Frequency stability ±30\u202f'
                                                 'ppm over -40\u202f°C to '
                                                 '+85\u202f°C for grade H.',
                                  'keywords': ['Frequency Stability',
                                               '±30 ppm',
                                               '-40°C ~ +85°C']},
                                 {'id': '7M_FSTAB_I',
                                  'pin': '',
                                  'type': 'frequency_stability',
                                  'value': 20,
                                  'unit': 'ppm',
                                  'description': 'Frequency stability ±20\u202f'
                                                 'ppm over -40\u202f°C to '
                                                 '+85\u202f°C for grade I.',
                                  'keywords': ['Frequency Stability',
                                               '±20 ppm',
                                               '-40°C ~ +85°C']},
                                 {'id': '7M_FSTAB_J',
                                  'pin': '',
                                  'type': 'frequency_stability',
                                  'value': 15,
                                  'unit': 'ppm',
                                  'description': 'Frequency stability ±15\u202f'
                                                 'ppm over -40\u202f°C to '
                                                 '+85\u202f°C for grade J.',
                                  'keywords': ['Frequency Stability',
                                               '±15 ppm',
                                               '-40°C ~ +85°C']},
                                 {'id': '7M_FSTAB_K',
                                  'pin': '',
                                  'type': 'frequency_stability',
                                  'value': 60,
                                  'unit': 'ppm',
                                  'description': 'Frequency stability ±60\u202f'
                                                 'ppm over -40\u202f°C to '
                                                 '+125\u202f°C for grade K.',
                                  'keywords': ['Frequency Stability',
                                               '±60 ppm',
                                               '-40°C ~ +125°C']},
                                 {'id': '7M_FTOL_A',
                                  'pin': '',
                                  'type': 'frequency_tolerance',
                                  'value': 30,
                                  'unit': 'ppm',
                                  'description': 'Frequency tolerance ±30\u202f'
                                                 'ppm at 25\u202f°C for grade '
                                                 'A.',
                                  'keywords': ['Frequency Tolerance',
                                               '±30ppm',
                                               'at 25°C']},
                                 {'id': '7M_FTOL_D',
                                  'pin': '',
                                  'type': 'frequency_tolerance',
                                  'value': 20,
                                  'unit': 'ppm',
                                  'description': 'Frequency tolerance ±20\u202f'
                                                 'ppm at 25\u202f°C for grade '
                                                 'D.',
                                  'keywords': ['Frequency Tolerance',
                                               '±20ppm',
                                               'at 25°C']},
                                 {'id': '7M_FTOL_E',
                                  'pin': '',
                                  'type': 'frequency_tolerance',
                                  'value': 10,
                                  'unit': 'ppm',
                                  'description': 'Frequency tolerance ±10\u202f'
                                                 'ppm at 25\u202f°C for grade '
                                                 'E.',
                                  'keywords': ['Frequency Tolerance',
                                               '±10ppm',
                                               'at 25°C']},
                                 {'id': '7M_ROHS_COMPLIANCE',
                                  'pin': '',
                                  'type': 'rohs_compliance',
                                  'value': None,
                                  'unit': None,
                                  'description': 'RoHS compliant and '
                                                 'lead‑free.',
                                  'keywords': ['RoHS', 'Pb free']},
                                 {'id': '7M_PACKAGING_TAPE_REEL',
                                  'pin': '',
                                  'type': 'packaging_method',
                                  'value': None,
                                  'unit': None,
                                  'description': 'Supplied in Tape & Reel '
                                                 'packaging.',
                                  'keywords': ['Packaging Method',
                                               'Tape & Reel']},
                                 {'id': '7M_REFLOW_PEAK_TEMP',
                                  'pin': '',
                                  'type': 'reflow_peak_temperature',
                                  'value': 260,
                                  'unit': '°C',
                                  'description': 'Peak reflow temperature '
                                                 '260\u202f°C ±10\u202f°C for '
                                                 '10\u202fseconds minimum.',
                                  'keywords': ['Reflow Profile',
                                               'Peak temperature',
                                               '260°C']},
                                 {'id': '7M_REFLOW_SOLDER_MELT',
                                  'pin': '',
                                  'type': 'reflow_solder_melt_temperature',
                                  'value': 220,
                                  'unit': '°C',
                                  'description': 'Solder melting point '
                                                 '220\u202f°C ±10\u202f°C for '
                                                 '60\u202fseconds minimum.',
                                  'keywords': ['Reflow Profile',
                                               'Solder melting point',
                                               '220°C']}]}]},
 'B220A': {'ics': [{'name': 'B220A',
                    'pins': ['ANODE', 'CATHODE'],
                    'constraints': [{'id': 'B220A_VRRM_MAX',
                                     'pin': '',
                                     'type': 'voltage_max',
                                     'value': 20,
                                     'unit': 'V',
                                     'description': 'Peak repetitive reverse '
                                                    'voltage rating',
                                     'keywords': ['Peak Repetitive Reverse '
                                                  'Voltage',
                                                  '20 V',
                                                  'B220A']},
                                    {'id': 'B220A_VRWM_MAX',
                                     'pin': '',
                                     'type': 'voltage_max',
                                     'value': 20,
                                     'unit': 'V',
                                     'description': 'Working peak reverse '
                                                    'voltage rating',
                                     'keywords': ['Working Peak Reverse '
                                                  'Voltage',
                                                  '20 V',
                                                  'B220A']},
                                    {'id': 'B220A_VR_MAX',
                                     'pin': '',
                                     'type': 'voltage_max',
                                     'value': 20,
                                     'unit': 'V',
                                     'description': 'DC blocking voltage '
                                                    'rating',
                                     'keywords': ['DC Blocking Voltage',
                                                  '20 V',
                                                  'B220A']},
                                    {'id': 'B220A_VR_RMS_MAX',
                                     'pin': '',
                                     'type': 'voltage_rms_max',
                                     'value': 14,
                                     'unit': 'V',
                                     'description': 'RMS reverse voltage '
                                                    'rating',
                                     'keywords': ['RMS Reverse Voltage',
                                                  '14 V',
                                                  'B220A']},
                                    {'id': 'B220A_IO_MAX',
                                     'pin': '',
                                     'type': 'current_max',
                                     'value': 2.0,
                                     'unit': 'A',
                                     'description': 'Average rectified output '
                                                    'current rating',
                                     'keywords': ['Average Rectified Output '
                                                  'Current',
                                                  '2.0 A',
                                                  'B220A']},
                                    {'id': 'B220A_IFSM_MAX',
                                     'pin': '',
                                     'type': 'current_max',
                                     'value': 50,
                                     'unit': 'A',
                                     'description': 'Non‑repetitive peak '
                                                    'forward surge current '
                                                    '(8.3\u202fms) rating',
                                     'keywords': ['Peak Forward Surge Current',
                                                  '50 A',
                                                  'B220A']},
                                    {'id': 'B220A_VF_MAX',
                                     'pin': '',
                                     'type': 'voltage_forward_max',
                                     'value': 0.5,
                                     'unit': 'V',
                                     'description': 'Maximum forward voltage '
                                                    'drop at IF = 2\u202fA, TA '
                                                    '= +25\u202f°C',
                                     'keywords': ['Forward Voltage Drop',
                                                  '0.5 V',
                                                  'B220A']},
                                    {'id': 'B220A_IR_MAX_T25',
                                     'pin': '',
                                     'type': 'current_max',
                                     'value': 0.5,
                                     'unit': 'mA',
                                     'description': 'Leakage current max at '
                                                    'rated reverse voltage, TA '
                                                    '= +25\u202f°C',
                                     'keywords': ['Leakage Current',
                                                  '0.5 mA',
                                                  '25°C']},
                                    {'id': 'B220A_IR_MAX_T100',
                                     'pin': '',
                                     'type': 'current_max',
                                     'value': 20,
                                     'unit': 'mA',
                                     'description': 'Leakage current max at '
                                                    'rated reverse voltage, TA '
                                                    '= +100\u202f°C',
                                     'keywords': ['Leakage Current',
                                                  '20 mA',
                                                  '100°C']},
                                    {'id': 'B220A_CT_TYP',
                                     'pin': '',
                                     'type': 'capacitance_typ',
                                     'value': 200,
                                     'unit': 'pF',
                                     'description': 'Typical total capacitance '
                                                    'at VR = 40\u202fV, f = '
                                                    '1\u202fMHz',
                                     'keywords': ['Total Capacitance',
                                                  '200 pF',
                                                  'B220A']},
                                    {'id': 'B220A_TJ_MIN',
                                     'pin': '',
                                     'type': 'temperature_min',
                                     'value': -65,
                                     'unit': '°C',
                                     'description': 'Minimum operating/storage '
                                                    'junction temperature',
                                     'keywords': ['Operating Temperature',
                                                  '-65 °C',
                                                  'B220A']},
                                    {'id': 'B220A_TJ_MAX',
                                     'pin': '',
                                     'type': 'temperature_max',
                                     'value': 150,
                                     'unit': '°C',
                                     'description': 'Maximum operating/storage '
                                                    'junction temperature',
                                     'keywords': ['Operating Temperature',
                                                  '150 °C',
                                                  'B220A']}]},
                   {'name': 'B230A',
                    'pins': ['ANODE', 'CATHODE'],
                    'constraints': [{'id': 'B230A_VRRM_MAX',
                                     'pin': '',
                                     'type': 'voltage_max',
                                     'value': 30,
                                     'unit': 'V',
                                     'description': 'Peak repetitive reverse '
                                                    'voltage rating',
                                     'keywords': ['Peak Repetitive Reverse '
                                                  'Voltage',
                                                  '30 V',
                                                  'B230A']},
                                    {'id': 'B230A_VRWM_MAX',
                                     'pin': '',
                                     'type': 'voltage_max',
                                     'value': 30,
                                     'unit': 'V',
                                     'description': 'Working peak reverse '
                                                    'voltage rating',
                                     'keywords': ['Working Peak Reverse '
                                                  'Voltage',
                                                  '30 V',
                                                  'B230A']},
                                    {'id': 'B230A_VR_MAX',
                                     'pin': '',
                                     'type': 'voltage_max',
                                     'value': 30,
                                     'unit': 'V',
                                     'description': 'DC blocking voltage '
                                                    'rating',
                                     'keywords': ['DC Blocking Voltage',
                                                  '30 V',
                                                  'B230A']},
                                    {'id': 'B230A_VR_RMS_MAX',
                                     'pin': '',
                                     'type': 'voltage_rms_max',
                                     'value': 21,
                                     'unit': 'V',
                                     'description': 'RMS reverse voltage '
                                                    'rating',
                                     'keywords': ['RMS Reverse Voltage',
                                                  '21 V',
                                                  'B230A']},
                                    {'id': 'B230A_IO_MAX',
                                     'pin': '',
                                     'type': 'current_max',
                                     'value': 2.0,
                                     'unit': 'A',
                                     'description': 'Average rectified output '
                                                    'current rating',
                                     'keywords': ['Average Rectified Output '
                                                  'Current',
                                                  '2.0 A',
                                                  'B230A']},
                                    {'id': 'B230A_IFSM_MAX',
                                     'pin': '',
                                     'type': 'current_max',
                                     'value': 50,
                                     'unit': 'A',
                                     'description': 'Non‑repetitive peak '
                                                    'forward surge current '
                                                    '(8.3\u202fms) rating',
                                     'keywords': ['Peak Forward Surge Current',
                                                  '50 A',
                                                  'B230A']},
                                    {'id': 'B230A_VF_MAX',
                                     'pin': '',
                                     'type': 'voltage_forward_max',
                                     'value': 0.5,
                                     'unit': 'V',
                                     'description': 'Maximum forward voltage '
                                                    'drop at IF = 2\u202fA, TA '
                                                    '= +25\u202f°C',
                                     'keywords': ['Forward Voltage Drop',
                                                  '0.5 V',
                                                  'B230A']},
                                    {'id': 'B230A_IR_MAX_T25',
                                     'pin': '',
                                     'type': 'current_max',
                                     'value': 0.5,
                                     'unit': 'mA',
                                     'description': 'Leakage current max at '
                                                    'rated reverse voltage, TA '
                                                    '= +25\u202f°C',
                                     'keywords': ['Leakage Current',
                                                  '0.5 mA',
                                                  '25°C']},
                                    {'id': 'B230A_IR_MAX_T100',
                                     'pin': '',
                                     'type': 'current_max',
                                     'value': 20,
                                     'unit': 'mA',
                                     'description': 'Leakage current max at '
                                                    'rated reverse voltage, TA '
                                                    '= +100\u202f°C',
                                     'keywords': ['Leakage Current',
                                                  '20 mA',
                                                  '100°C']},
                                    {'id': 'B230A_CT_TYP',
                                     'pin': '',
                                     'type': 'capacitance_typ',
                                     'value': 200,
                                     'unit': 'pF',
                                     'description': 'Typical total capacitance '
                                                    'at VR = 40\u202fV, f = '
                                                    '1\u202fMHz',
                                     'keywords': ['Total Capacitance',
                                                  '200 pF',
                                                  'B230A']},
                                    {'id': 'B230A_TJ_MIN',
                                     'pin': '',
                                     'type': 'temperature_min',
                                     'value': -65,
                                     'unit': '°C',
                                     'description': 'Minimum operating/storage '
                                                    'junction temperature',
                                     'keywords': ['Operating Temperature',
                                                  '-65 °C',
                                                  'B230A']},
                                    {'id': 'B230A_TJ_MAX',
                                     'pin': '',
                                     'type': 'temperature_max',
                                     'value': 150,
                                     'unit': '°C',
                                     'description': 'Maximum operating/storage '
                                                    'junction temperature',
                                     'keywords': ['Operating Temperature',
                                                  '150 °C',
                                                  'B230A']}]},
                   {'name': 'B240A',
                    'pins': ['ANODE', 'CATHODE'],
                    'constraints': [{'id': 'B240A_VRRM_MAX',
                                     'pin': '',
                                     'type': 'voltage_max',
                                     'value': 40,
                                     'unit': 'V',
                                     'description': 'Peak repetitive reverse '
                                                    'voltage rating',
                                     'keywords': ['Peak Repetitive Reverse '
                                                  'Voltage',
                                                  '40 V',
                                                  'B240A']},
                                    {'id': 'B240A_VRWM_MAX',
                                     'pin': '',
                                     'type': 'voltage_max',
                                     'value': 40,
                                     'unit': 'V',
                                     'description': 'Working peak reverse '
                                                    'voltage rating',
                                     'keywords': ['Working Peak Reverse '
                                                  'Voltage',
                                                  '40 V',
                                                  'B240A']},
                                    {'id': 'B240A_VR_MAX',
                                     'pin': '',
                                     'type': 'voltage_max',
                                     'value': 40,
                                     'unit': 'V',
                                     'description': 'DC blocking voltage '
                                                    'rating',
                                     'keywords': ['DC Blocking Voltage',
                                                  '40 V',
                                                  'B240A']},
                                    {'id': 'B240A_VR_RMS_MAX',
                                     'pin': '',
                                     'type': 'voltage_rms_max',
                                     'value': 28,
                                     'unit': 'V',
                                     'description': 'RMS reverse voltage '
                                                    'rating',
                                     'keywords': ['RMS Reverse Voltage',
                                                  '28 V',
                                                  'B240A']},
                                    {'id': 'B240A_IO_MAX',
                                     'pin': '',
                                     'type': 'current_max',
                                     'value': 2.0,
                                     'unit': 'A',
                                     'description': 'Average rectified output '
                                                    'current rating',
                                     'keywords': ['Average Rectified Output '
                                                  'Current',
                                                  '2.0 A',
                                                  'B240A']},
                                    {'id': 'B240A_IFSM_MAX',
                                     'pin': '',
                                     'type': 'current_max',
                                     'value': 50,
                                     'unit': 'A',
                                     'description': 'Non‑repetitive peak '
                                                    'forward surge current '
                                                    '(8.3\u202fms) rating',
                                     'keywords': ['Peak Forward Surge Current',
                                                  '50 A',
                                                  'B240A']},
                                    {'id': 'B240A_VF_MAX',
                                     'pin': '',
                                     'type': 'voltage_forward_max',
                                     'value': 0.5,
                                     'unit': 'V',
                                     'description': 'Maximum forward voltage '
                                                    'drop at IF = 2\u202fA, TA '
                                                    '= +25\u202f°C',
                                     'keywords': ['Forward Voltage Drop',
                                                  '0.5 V',
                                                  'B240A']},
                                    {'id': 'B240A_IR_MAX_T25',
                                     'pin': '',
                                     'type': 'current_max',
                                     'value': 0.5,
                                     'unit': 'mA',
                                     'description': 'Leakage current max at '
                                                    'rated reverse voltage, TA '
                                                    '= +25\u202f°C',
                                     'keywords': ['Leakage Current',
                                                  '0.5 mA',
                                                  '25°C']},
                                    {'id': 'B240A_IR_MAX_T100',
                                     'pin': '',
                                     'type': 'current_max',
                                     'value': 20,
                                     'unit': 'mA',
                                     'description': 'Leakage current max at '
                                                    'rated reverse voltage, TA '
                                                    '= +100\u202f°C',
                                     'keywords': ['Leakage Current',
                                                  '20 mA',
                                                  '100°C']},
                                    {'id': 'B240A_CT_TYP',
                                     'pin': '',
                                     'type': 'capacitance_typ',
                                     'value': 200,
                                     'unit': 'pF',
                                     'description': 'Typical total capacitance '
                                                    'at VR = 40\u202fV, f = '
                                                    '1\u202fMHz',
                                     'keywords': ['Total Capacitance',
                                                  '200 pF',
                                                  'B240A']},
                                    {'id': 'B240A_TJ_MIN',
                                     'pin': '',
                                     'type': 'temperature_min',
                                     'value': -65,
                                     'unit': '°C',
                                     'description': 'Minimum operating/storage '
                                                    'junction temperature',
                                     'keywords': ['Operating Temperature',
                                                  '-65 °C',
                                                  'B240A']},
                                    {'id': 'B240A_TJ_MAX',
                                     'pin': '',
                                     'type': 'temperature_max',
                                     'value': 150,
                                     'unit': '°C',
                                     'description': 'Maximum operating/storage '
                                                    'junction temperature',
                                     'keywords': ['Operating Temperature',
                                                  '150 °C',
                                                  'B240A']}]},
                   {'name': 'B250A',
                    'pins': ['ANODE', 'CATHODE'],
                    'constraints': [{'id': 'B250A_VRRM_MAX',
                                     'pin': '',
                                     'type': 'voltage_max',
                                     'value': 50,
                                     'unit': 'V',
                                     'description': 'Peak repetitive reverse '
                                                    'voltage rating',
                                     'keywords': ['Peak Repetitive Reverse '
                                                  'Voltage',
                                                  '50 V',
                                                  'B250A']},
                                    {'id': 'B250A_VRWM_MAX',
                                     'pin': '',
                                     'type': 'voltage_max',
                                     'value': 50,
                                     'unit': 'V',
                                     'description': 'Working peak reverse '
                                                    'voltage rating',
                                     'keywords': ['Working Peak Reverse '
                                                  'Voltage',
                                                  '50 V',
                                                  'B250A']},
                                    {'id': 'B250A_VR_MAX',
                                     'pin': '',
                                     'type': 'voltage_max',
                                     'value': 50,
                                     'unit': 'V',
                                     'description': 'DC blocking voltage '
                                                    'rating',
                                     'keywords': ['DC Blocking Voltage',
                                                  '50 V',
                                                  'B250A']},
                                    {'id': 'B250A_VR_RMS_MAX',
                                     'pin': '',
                                     'type': 'voltage_rms_max',
                                     'value': 35,
                                     'unit': 'V',
                                     'description': 'RMS reverse voltage '
                                                    'rating',
                                     'keywords': ['RMS Reverse Voltage',
                                                  '35 V',
                                                  'B250A']},
                                    {'id': 'B250A_IO_MAX',
                                     'pin': '',
                                     'type': 'current_max',
                                     'value': 2.0,
                                     'unit': 'A',
                                     'description': 'Average rectified output '
                                                    'current rating',
                                     'keywords': ['Average Rectified Output '
                                                  'Current',
                                                  '2.0 A',
                                                  'B250A']},
                                    {'id': 'B250A_IFSM_MAX',
                                     'pin': '',
                                     'type': 'current_max',
                                     'value': 50,
                                     'unit': 'A',
                                     'description': 'Non‑repetitive peak '
                                                    'forward surge current '
                                                    '(8.3\u202fms) rating',
                                     'keywords': ['Peak Forward Surge Current',
                                                  '50 A',
                                                  'B250A']},
                                    {'id': 'B250A_VF_MAX',
                                     'pin': '',
                                     'type': 'voltage_forward_max',
                                     'value': 0.7,
                                     'unit': 'V',
                                     'description': 'Maximum forward voltage '
                                                    'drop at IF = 2\u202fA, TA '
                                                    '= +25\u202f°C',
                                     'keywords': ['Forward Voltage Drop',
                                                  '0.7 V',
                                                  'B250A']},
                                    {'id': 'B250A_IR_MAX_T25',
                                     'pin': '',
                                     'type': 'current_max',
                                     'value': 0.5,
                                     'unit': 'mA',
                                     'description': 'Leakage current max at '
                                                    'rated reverse voltage, TA '
                                                    '= +25\u202f°C',
                                     'keywords': ['Leakage Current',
                                                  '0.5 mA',
                                                  '25°C']},
                                    {'id': 'B250A_IR_MAX_T100',
                                     'pin': '',
                                     'type': 'current_max',
                                     'value': 20,
                                     'unit': 'mA',
                                     'description': 'Leakage current max at '
                                                    'rated reverse voltage, TA '
                                                    '= +100\u202f°C',
                                     'keywords': ['Leakage Current',
                                                  '20 mA',
                                                  '100°C']},
                                    {'id': 'B250A_CT_TYP',
                                     'pin': '',
                                     'type': 'capacitance_typ',
                                     'value': 200,
                                     'unit': 'pF',
                                     'description': 'Typical total capacitance '
                                                    'at VR = 40\u202fV, f = '
                                                    '1\u202fMHz',
                                     'keywords': ['Total Capacitance',
                                                  '200 pF',
                                                  'B250A']},
                                    {'id': 'B250A_TJ_MIN',
                                     'pin': '',
                                     'type': 'temperature_min',
                                     'value': -65,
                                     'unit': '°C',
                                     'description': 'Minimum operating/storage '
                                                    'junction temperature',
                                     'keywords': ['Operating Temperature',
                                                  '-65 °C',
                                                  'B250A']},
                                    {'id': 'B250A_TJ_MAX',
                                     'pin': '',
                                     'type': 'temperature_max',
                                     'value': 150,
                                     'unit': '°C',
                                     'description': 'Maximum operating/storage '
                                                    'junction temperature',
                                     'keywords': ['Operating Temperature',
                                                  '150 °C',
                                                  'B250A']}]},
                   {'name': 'B260A',
                    'pins': ['ANODE', 'CATHODE'],
                    'constraints': [{'id': 'B260A_VRRM_MAX',
                                     'pin': '',
                                     'type': 'voltage_max',
                                     'value': 60,
                                     'unit': 'V',
                                     'description': 'Peak repetitive reverse '
                                                    'voltage rating',
                                     'keywords': ['Peak Repetitive Reverse '
                                                  'Voltage',
                                                  '60 V',
                                                  'B260A']},
                                    {'id': 'B260A_VRWM_MAX',
                                     'pin': '',
                                     'type': 'voltage_max',
                                     'value': 60,
                                     'unit': 'V',
                                     'description': 'Working peak reverse '
                                                    'voltage rating',
                                     'keywords': ['Working Peak Reverse '
                                                  'Voltage',
                                                  '60 V',
                                                  'B260A']},
                                    {'id': 'B260A_VR_MAX',
                                     'pin': '',
                                     'type': 'voltage_max',
                                     'value': 60,
                                     'unit': 'V',
                                     'description': 'DC blocking voltage '
                                                    'rating',
                                     'keywords': ['DC Blocking Voltage',
                                                  '60 V',
                                                  'B260A']},
                                    {'id': 'B260A_VR_RMS_MAX',
                                     'pin': '',
                                     'type': 'voltage_rms_max',
                                     'value': 42,
                                     'unit': 'V',
                                     'description': 'RMS reverse voltage '
                                                    'rating',
                                     'keywords': ['RMS Reverse Voltage',
                                                  '42 V',
                                                  'B260A']},
                                    {'id': 'B260A_IO_MAX',
                                     'pin': '',
                                     'type': 'current_max',
                                     'value': 2.0,
                                     'unit': 'A',
                                     'description': 'Average rectified output '
                                                    'current rating',
                                     'keywords': ['Average Rectified Output '
                                                  'Current',
                                                  '2.0 A',
                                                  'B260A']},
                                    {'id': 'B260A_IFSM_MAX',
                                     'pin': '',
                                     'type': 'current_max',
                                     'value': 50,
                                     'unit': 'A',
                                     'description': 'Non‑repetitive peak '
                                                    'forward surge current '
                                                    '(8.3\u202fms) rating',
                                     'keywords': ['Peak Forward Surge Current',
                                                  '50 A',
                                                  'B260A']},
                                    {'id': 'B260A_VF_MAX',
                                     'pin': '',
                                     'type': 'voltage_forward_max',
                                     'value': 0.7,
                                     'unit': 'V',
                                     'description': 'Maximum forward voltage '
                                                    'drop at IF = 2\u202fA, TA '
                                                    '= +25\u202f°C',
                                     'keywords': ['Forward Voltage Drop',
                                                  '0.7 V',
                                                  'B260A']},
                                    {'id': 'B260A_IR_MAX_T25',
                                     'pin': '',
                                     'type': 'current_max',
                                     'value': 0.5,
                                     'unit': 'mA',
                                     'description': 'Leakage current max at '
                                                    'rated reverse voltage, TA '
                                                    '= +25\u202f°C',
                                     'keywords': ['Leakage Current',
                                                  '0.5 mA',
                                                  '25°C']},
                                    {'id': 'B260A_IR_MAX_T100',
                                     'pin': '',
                                     'type': 'current_max',
                                     'value': 20,
                                     'unit': 'mA',
                                     'description': 'Leakage current max at '
                                                    'rated reverse voltage, TA '
                                                    '= +100\u202f°C',
                                     'keywords': ['Leakage Current',
                                                  '20 mA',
                                                  '100°C']},
                                    {'id': 'B260A_CT_TYP',
                                     'pin': '',
                                     'type': 'capacitance_typ',
                                     'value': 200,
                                     'unit': 'pF',
                                     'description': 'Typical total capacitance '
                                                    'at VR = 40\u202fV, f = '
                                                    '1\u202fMHz',
                                     'keywords': ['Total Capacitance',
                                                  '200 pF',
                                                  'B260A']},
                                    {'id': 'B260A_TJ_MIN',
                                     'pin': '',
                                     'type': 'temperature_min',
                                     'value': -65,
                                     'unit': '°C',
                                     'description': 'Minimum operating/storage '
                                                    'junction temperature',
                                     'keywords': ['Operating Temperature',
                                                  '-65 °C',
                                                  'B260A']},
                                    {'id': 'B260A_TJ_MAX',
                                     'pin': '',
                                     'type': 'temperature_max',
                                     'value': 150,
                                     'unit': '°C',
                                     'description': 'Maximum operating/storage '
                                                    'junction temperature',
                                     'keywords': ['Operating Temperature',
                                                  '150 °C',
                                                  'B260A']}]}]},
 'ISL81401_ISL81401A': {'ics': [{'name': 'ISL81401',
                                 'pins': ['VIN',
                                          'VOUT',
                                          'EN',
                                          'UVLO',
                                          'PGOOD',
                                          'FB_OUT',
                                          'CS+',
                                          'CS-',
                                          'SS/TRK',
                                          'IMON_OUT',
                                          'IMON_IN',
                                          'EXTBIAS',
                                          'VDD',
                                          'VCC5V',
                                          'BOOT1',
                                          'BOOT2',
                                          'UG1',
                                          'UG2',
                                          'PHASE1',
                                          'PHASE2',
                                          'LG1',
                                          'LG2',
                                          'PGND',
                                          'OC_MODE',
                                          'COMP',
                                          'ISEN+',
                                          'ISEN-',
                                          'A1',
                                          'A2',
                                          'CLKOUT',
                                          'DITHER',
                                          'REF',
                                          'RT',
                                          'SYNC',
                                          'PWM',
                                          'FB_IN',
                                          'FB_OUT',
                                          'RST'],
                                 'constraints': [{'id': 'ISL81401_VIN_MIN',
                                                  'pin': 'VIN',
                                                  'type': 'min_voltage',
                                                  'value': 4.5,
                                                  'unit': 'V',
                                                  'description': 'Minimum '
                                                                 'input '
                                                                 'voltage that '
                                                                 'the device '
                                                                 'can operate '
                                                                 'with.',
                                                  'keywords': ['wide input '
                                                               'voltage range',
                                                               '4.5V']},
                                                 {'id': 'ISL81401_VIN_MAX',
                                                  'pin': 'VIN',
                                                  'type': 'max_voltage',
                                                  'value': 40,
                                                  'unit': 'V',
                                                  'description': 'Maximum '
                                                                 'input '
                                                                 'voltage that '
                                                                 'the device '
                                                                 'can '
                                                                 'tolerate.',
                                                  'keywords': ['wide input '
                                                               'voltage range',
                                                               '40V']},
                                                 {'id': 'ISL81401_VOUT_MIN',
                                                  'pin': 'VOUT',
                                                  'type': 'min_voltage',
                                                  'value': 0.8,
                                                  'unit': 'V',
                                                  'description': 'Minimum '
                                                                 'regulated '
                                                                 'output '
                                                                 'voltage.',
                                                  'keywords': ['wide output '
                                                               'voltage range',
                                                               '0.8V']},
                                                 {'id': 'ISL81401_VOUT_MAX',
                                                  'pin': 'VOUT',
                                                  'type': 'max_voltage',
                                                  'value': 40,
                                                  'unit': 'V',
                                                  'description': 'Maximum '
                                                                 'regulated '
                                                                 'output '
                                                                 'voltage.',
                                                  'keywords': ['wide output '
                                                               'voltage range',
                                                               '40V']},
                                                 {'id': 'ISL81401_F0_MIN',
                                                  'pin': '',
                                                  'type': 'min_frequency',
                                                  'value': 100,
                                                  'unit': 'kHz',
                                                  'description': 'Minimum '
                                                                 'programmable '
                                                                 'switching '
                                                                 'frequency.',
                                                  'keywords': ['programmable '
                                                               'frequency',
                                                               '100kHz']},
                                                 {'id': 'ISL81401_F0_MAX',
                                                  'pin': '',
                                                  'type': 'max_frequency',
                                                  'value': 600,
                                                  'unit': 'kHz',
                                                  'description': 'Maximum '
                                                                 'programmable '
                                                                 'switching '
                                                                 'frequency.',
                                                  'keywords': ['programmable '
                                                               'frequency',
                                                               '600kHz']},
                                                 {'id': 'ISL81401_QUISCENT_CURRENT',
                                                  'pin': 'EN',
                                                  'type': 'quiescent_current',
                                                  'value': 2.7,
                                                  'unit': 'µA',
                                                  'description': 'Low shutdown '
                                                                 '(quiescent) '
                                                                 'current when '
                                                                 'the device '
                                                                 'is disabled.',
                                                  'keywords': ['low shut down '
                                                               'current',
                                                               '2.7µA']},
                                                 {'id': 'ISL81401_EXTBIAS_VOLTAGE_MIN',
                                                  'pin': 'EXTBIAS',
                                                  'type': 'min_voltage',
                                                  'value': 5,
                                                  'unit': 'V',
                                                  'description': 'Minimum '
                                                                 'external '
                                                                 'bias supply '
                                                                 'voltage for '
                                                                 'higher '
                                                                 'efficiency '
                                                                 'operation.',
                                                  'keywords': ['external bias',
                                                               '5V']},
                                                 {'id': 'ISL81401_EXTBIAS_VOLTAGE_MAX',
                                                  'pin': 'EXTBIAS',
                                                  'type': 'max_voltage',
                                                  'value': 36,
                                                  'unit': 'V',
                                                  'description': 'Maximum '
                                                                 'external '
                                                                 'bias supply '
                                                                 'voltage for '
                                                                 'higher '
                                                                 'efficiency '
                                                                 'operation.',
                                                  'keywords': ['external bias',
                                                               '36V']}]},
                                {'name': 'ISL81401A',
                                 'pins': ['VIN',
                                          'VOUT',
                                          'EN',
                                          'UVLO',
                                          'PGOOD',
                                          'FB_OUT',
                                          'CS+',
                                          'CS-',
                                          'SS/TRK',
                                          'IMON_OUT',
                                          'IMON_IN',
                                          'EXTBIAS',
                                          'VDD',
                                          'VCC5V',
                                          'BOOT1',
                                          'BOOT2',
                                          'UG1',
                                          'UG2',
                                          'PHASE1',
                                          'PHASE2',
                                          'LG1',
                                          'LG2',
                                          'PGND',
                                          'OC_MODE',
                                          'COMP',
                                          'ISEN+',
                                          'ISEN-',
                                          'A1',
                                          'A2',
                                          'CLKOUT',
                                          'DITHER',
                                          'REF',
                                          'RT',
                                          'SYNC',
                                          'PWM',
                                          'FB_IN',
                                          'FB_OUT',
                                          'RST'],
                                 'constraints': [{'id': 'ISL81401A_VIN_MIN',
                                                  'pin': 'VIN',
                                                  'type': 'min_voltage',
                                                  'value': 4.5,
                                                  'unit': 'V',
                                                  'description': 'Minimum '
                                                                 'input '
                                                                 'voltage for '
                                                                 'the '
                                                                 'unidirectional '
                                                                 'version.',
                                                  'keywords': ['wide input '
                                                               'voltage range',
                                                               '4.5V']},
                                                 {'id': 'ISL81401A_VIN_MAX',
                                                  'pin': 'VIN',
                                                  'type': 'max_voltage',
                                                  'value': 40,
                                                  'unit': 'V',
                                                  'description': 'Maximum '
                                                                 'input '
                                                                 'voltage for '
                                                                 'the '
                                                                 'unidirectional '
                                                                 'version.',
                                                  'keywords': ['wide input '
                                                               'voltage range',
                                                               '40V']},
                                                 {'id': 'ISL81401A_VOUT_MIN',
                                                  'pin': 'VOUT',
                                                  'type': 'min_voltage',
                                                  'value': 0.8,
                                                  'unit': 'V',
                                                  'description': 'Minimum '
                                                                 'regulated '
                                                                 'output '
                                                                 'voltage for '
                                                                 'the '
                                                                 'unidirectional '
                                                                 'version.',
                                                  'keywords': ['wide output '
                                                               'voltage range',
                                                               '0.8V']},
                                                 {'id': 'ISL81401A_VOUT_MAX',
                                                  'pin': 'VOUT',
                                                  'type': 'max_voltage',
                                                  'value': 40,
                                                  'unit': 'V',
                                                  'description': 'Maximum '
                                                                 'regulated '
                                                                 'output '
                                                                 'voltage for '
                                                                 'the '
                                                                 'unidirectional '
                                                                 'version.',
                                                  'keywords': ['wide output '
                                                               'voltage range',
                                                               '40V']},
                                                 {'id': 'ISL81401A_F0_MIN',
                                                  'pin': '',
                                                  'type': 'min_frequency',
                                                  'value': 100,
                                                  'unit': 'kHz',
                                                  'description': 'Minimum '
                                                                 'programmable '
                                                                 'switching '
                                                                 'frequency '
                                                                 'for the '
                                                                 'unidirectional '
                                                                 'device.',
                                                  'keywords': ['programmable '
                                                               'frequency',
                                                               '100kHz']},
                                                 {'id': 'ISL81401A_F0_MAX',
                                                  'pin': '',
                                                  'type': 'max_frequency',
                                                  'value': 600,
                                                  'unit': 'kHz',
                                                  'description': 'Maximum '
                                                                 'programmable '
                                                                 'switching '
                                                                 'frequency '
                                                                 'for the '
                                                                 'unidirectional '
                                                                 'device.',
                                                  'keywords': ['programmable '
                                                               'frequency',
                                                               '600kHz']},
                                                 {'id': 'ISL81401A_QUISCENT_CURRENT',
                                                  'pin': 'EN',
                                                  'type': 'quiescent_current',
                                                  'value': 2.7,
                                                  'unit': 'µA',
                                                  'description': 'Low shutdown '
                                                                 'current when '
                                                                 'disabled, '
                                                                 'same as '
                                                                 'bidirectional '
                                                                 'version.',
                                                  'keywords': ['low shut down '
                                                               'current',
                                                               '2.7µA']},
                                                 {'id': 'ISL81401A_EXTBIAS_VOLTAGE_MIN',
                                                  'pin': 'EXTBIAS',
                                                  'type': 'min_voltage',
                                                  'value': 5,
                                                  'unit': 'V',
                                                  'description': 'Minimum '
                                                                 'external '
                                                                 'bias voltage '
                                                                 'for higher '
                                                                 'efficiency '
                                                                 'operation.',
                                                  'keywords': ['external bias',
                                                               '5V']},
                                                 {'id': 'ISL81401A_EXTBIAS_VOLTAGE_MAX',
                                                  'pin': 'EXTBIAS',
                                                  'type': 'max_voltage',
                                                  'value': 36,
                                                  'unit': 'V',
                                                  'description': 'Maximum '
                                                                 'external '
                                                                 'bias voltage '
                                                                 'for higher '
                                                                 'efficiency '
                                                                 'operation.',
                                                  'keywords': ['external bias',
                                                               '36V']}]}]}}
