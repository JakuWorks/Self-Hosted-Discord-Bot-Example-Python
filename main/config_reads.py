from os.path import abspath, dirname
from configparser import ConfigParser, SectionProxy


class ConfigReader:
    def __init__(self) -> None:
        self.config: ConfigParser = ConfigParser()
        self.PathConfig = r".\config.ini"
        self.PathConfigParentAbs: str = abspath(dirname(self.PathConfig))
        self.config.read(self.PathConfig)

        self.update_values()

    def update_values(self) -> None:
        self.config_main_n: str = "MAIN"
        self.config_main: SectionProxy = self.config["MAIN"]

        # Paths
        self.PathAssetsFolder_n: str = "PathAssetsFolder"
        self.PathAssetsFolder: str = self.config_main.get(self.PathAssetsFolder_n)

        self.PathMainScript_n: str = "PathMainScript"
        self.PathMainScript: str = self.config_main.get(self.PathMainScript_n)

        self.PathRequirements_n: str = "PathRequirements"
        self.PathRequirements: str = self.config_main.get(self.PathRequirements_n)

        self.PathVenvActivateScript_n: str = "PathVenvActivateScript"
        self.PathVenvActivateScript: str = self.config_main.get(self.PathVenvActivateScript_n)

        self.PathResetToken_n: str = "PathResetToken"
        self.PathResetToken: str = self.config_main.get(self.PathResetToken_n)

        # Other
        self.ClearTokenIfBad_n: str = "ClearTokenIfBad"
        self.ClearTokenIfBad: bool = bool(int(self.config_main.get(self.ClearTokenIfBad_n)))

        self.MinimumPythonVersion_n: str = "MinimumPythonVersion"
        self.MinimumPythonVersion: str = self.config_main.get(self.MinimumPythonVersion_n)

        self.salt_base64encoded_utf8_n: str = "salt_base64encoded_utf8"
        self.salt_base64encoded_utf8: str = self.config_main.get(self.salt_base64encoded_utf8_n)

        self.token_ciphered_base64encoded_utf8_n: str = "token_ciphered_base64encoded_utf8"
        self.token_ciphered_base64encoded_utf8: str = self.config_main.get(self.token_ciphered_base64encoded_utf8_n)

        self.token_ciphered_iv_base64encoded_utf8_n: str = "token_ciphered_iv_base64encoded_utf8"
        self.token_ciphered_iv_base64encoded_utf8: str = self.config_main.get(self.token_ciphered_iv_base64encoded_utf8_n)

    def edit_key(self, section: str, key: str, value: str):
        self.config[section][key] = value
        self.update_values()

        with open(self.PathConfig, 'wt') as f:
            self.config.write(f)


config_reads = ConfigReader()
