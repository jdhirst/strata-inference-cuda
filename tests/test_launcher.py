import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


loader = importlib.machinery.SourceFileLoader('launcher', str(Path(__file__).parents[1] / 'strata-inference'))
spec = importlib.util.spec_from_loader(loader.name, loader)
launcher = importlib.util.module_from_spec(spec)
loader.exec_module(launcher)


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        real = self.root / 'external-model-drive'
        real.mkdir()
        models = self.root / '.models'
        models.symlink_to(real, target_is_directory=True)
        self.models = models
        self.addCleanup(patch.stopall)
        patch.object(launcher, 'MODELS', models).start()
        patch.dict(os.environ, {'XDG_CONFIG_HOME': str(self.root / 'config'),
                                'XDG_STATE_HOME': str(self.root / 'state')}).start()
        patch.dict('sys.modules', {'gguf_reader': SimpleNamespace(
            GGUFFile=lambda path: SimpleNamespace(tensors=[SimpleNamespace(name='per_layer_token_embd.weight')]))}).start()

    def call(self, *args):
        with patch('sys.argv', ['strata-inference', *map(str, args)]):
            launcher.main()

    def prepared(self):
        model = self.models / 'example-iq3-s'
        (model / 'strata/pack/tokenizer').mkdir(parents=True)
        gguf = model / 'first.gguf'
        gguf.touch()
        (self.models / 'qwen3.8-flash-next-mtp/strata/rt').mkdir(parents=True)
        data = self.root / 'data'
        data.mkdir()
        (data / 'expert-profile.bin').write_bytes(b'profile')
        patch.object(launcher, 'DATA', data).start()
        return gguf

    def test_model_root_symlink_is_accepted_and_outside_path_rejected(self):
        gguf = self.prepared()
        self.assertEqual(launcher.model_path(str(gguf)), gguf.resolve())
        with self.assertRaises(ValueError):
            launcher.model_path(self.root / 'outside.gguf')

    def test_config_is_writable_outside_application_and_keeps_models_on_model_drive(self):
        gguf = self.prepared()
        self.call('configure', gguf, '--context', '32768')
        config = self.root / 'config/strata-inference/example-iq3-s.json'
        settings = json.loads(config.read_text())
        self.assertEqual(settings['port'], 8082)
        self.assertEqual(settings['host'], '127.0.0.1')
        self.assertEqual(settings['exe'], '/usr/bin/strata-inference-engine')
        self.assertEqual(settings['cwd'], str(self.root / 'state/strata-inference'))
        self.assertEqual(settings['args'][settings['args'].index('--native') + 1], str(gguf.resolve()))
        self.assertTrue(self.models.is_symlink())

    def test_existing_configuration_is_preserved(self):
        gguf = self.prepared()
        self.call('configure', gguf)
        config = self.root / 'config/strata-inference/example-iq3-s.json'
        config.write_text('user custom configuration')
        with self.assertRaises(SystemExit):
            self.call('configure', gguf)
        self.assertEqual(config.read_text(), 'user custom configuration')

    def test_network_binding_needs_key_before_loading_config_or_engine(self):
        with patch.dict(os.environ, {'STRATA_API_KEY': ''}):
            with self.assertRaises(SystemExit):
                self.call('serve', '--config', 'missing.json', '--host', '0.0.0.0')

    def test_prepare_never_downloads_or_writes_into_application(self):
        gguf = self.prepared()
        with patch.object(launcher, 'tool') as tool:
            self.call('prepare', gguf)
        tool.assert_called_once_with('iq_pack', '--gguf', gguf.resolve(), '--out',
                                     gguf.resolve().parent / 'strata/pack')

    def test_lookup_table_is_found_in_second_shard(self):
        model = self.models / 'split-model'
        model.mkdir()
        first = model / 'model-00001-of-00002.gguf'
        second = model / 'model-00002-of-00002.gguf'
        first.touch()
        second.touch()
        def reader(path):
            names = ['per_layer_token_embd.weight'] if path == second else ['token_embd.weight']
            return SimpleNamespace(tensors=[SimpleNamespace(name=name) for name in names])
        with patch.dict('sys.modules', {'gguf_reader': SimpleNamespace(GGUFFile=reader)}):
            self.assertEqual(launcher.ple_shard(first), second)
        second.unlink()
        with self.assertRaises(ValueError):
            launcher.ple_shard(first)


if __name__ == '__main__':
    unittest.main()
