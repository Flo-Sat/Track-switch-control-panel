import time

IODIRA = 0x00
IODIRB = 0x01
OLATB  = 0x14  # position droit
OLATA  = 0x15  # position dévié

try:
    import smbus
    _bus = smbus.SMBus(1)
    AVAILABLE = True
    print('I2C initialisé')
except Exception as e:
    _bus = None
    AVAILABLE = False
    print(f'I2C non disponible (mode simulation) : {e}')


def pulse(i2c_addr, register, spec):
    if not AVAILABLE:
        return
    try:
        _bus.write_byte_data(i2c_addr, register, spec)
        time.sleep(0.3)
        _bus.write_byte_data(i2c_addr, register, 0)
    except Exception as e:
        print(f'Erreur I2C {hex(i2c_addr)} reg={hex(register)} spec={spec} : {e}')
        try:
            _bus.write_byte_data(i2c_addr, register, 0)
        except Exception:
            pass


def init_com(dashboard_data):
    """Configure tous les MCP23017 en sortie (IODIRA/B = 0x00)."""
    if not AVAILABLE:
        return
    unique_chips = set(int(d['i2c'], 16) for d in dashboard_data.values())
    for addr in sorted(unique_chips):
        try:
            _bus.write_byte_data(addr, IODIRA, 0x00)
            _bus.write_byte_data(addr, IODIRB, 0x00)
            print(f'MCP23017 {hex(addr)} initialisé')
        except Exception as e:
            print(f'Erreur init {hex(addr)} : {e}')


def reset_all(dashboard_data, position_data):
    """Remet tous les aiguillages en position droit (OLATA) au démarrage."""
    if not AVAILABLE:
        return
    print('Reset de tous les aiguillages...')
    for id, data in dashboard_data.items():
        if(position_data[id]["inverse"] == 0):

            pulse(int(data['i2c'], 16), OLATA, data['spec'])
        else:
            pulse(int(data['i2c'], 16), OLATB, data['spec'])
    print('Reset terminé')
