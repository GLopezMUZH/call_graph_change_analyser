# %%
import pytest
import logging

from imp import reload

from ..call_graph_change_analyser.models import FileData, FileImport
from ..call_graph_change_analyser.repository_mining_util import parse_xml_diffs, get_file_imports

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# %%
def test_get_file_imports():
    file_path = '.\\example_project\\current\\UavcanNode.cpp'
    file_contents = ''
    with open(file_path, "r") as f:
        file_contents = f.read()

    file_data = FileData(file_path)
    print(file_data)

    fis = get_file_imports(source_code=file_contents, mod_file_data=file_data)
    for fi in fis:
        print(fi.get_src_file_name)

    fis_should = ['UavcanNode.hpp',
                  'boot_app_shared.h',
                  'boot_alt_app_shared.h',
                  'drv_watchdog.h',
                  'geo.h',
                  'version.h',
                  'BatteryInfo.hpp',
                  'FlowMeasurement.hpp',
                  'GnssFix2.hpp',
                  'MagneticFieldStrength2.hpp',
                  'RangeSensorMeasurement.hpp',
                  'RawAirData.hpp',
                  'SafetyButton.hpp',
                  'StaticPressure.hpp',
                  'StaticTemperature.hpp',
                  'BeepCommand.hpp',
                  'LightsCommand.hpp',
                  'RTCMStream.hpp']
