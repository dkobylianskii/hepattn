from pathlib import Path

import matplotlib.pyplot as plt
import pytest
import torch

from hepattn.experiments.trackml.data import TrackMLDataset
from hepattn.experiments.trackml.eval.plot_event import plot_trackml_event_reconstruction
from hepattn.experiments.trackml.prep import preprocess
from hepattn.models.matcher import Matcher

plt.rcParams["figure.dpi"] = 300


class TestTrackMLEvent:
    @pytest.fixture
    def trackml_event(self):
        input_fields = {
            "hit": [
                "x",
                "y",
                "z",
                "r",
                "eta",
                "phi",
                "u",
                "v",
                "charge_frac",
                "leta",
                "lphi",
                "lx",
                "ly",
                "lz",
                "geta",
                "gphi",
            ]
        }

        target_fields = {
            "particle": ["pt", "eta", "phi"],
        }

        dirpath = "data/trackml/prepped/"
        num_events = 2
        hit_volume_ids = [8]
        particle_min_pt = 1.0
        particle_max_abs_eta = 2.5
        particle_min_num_hits = 3
        event_max_num_particles = 1000

        dataset = TrackMLDataset(
            dirpath=dirpath,
            inputs=input_fields,
            targets=target_fields,
            num_events=num_events,
            hit_volume_ids=hit_volume_ids,
            particle_min_pt=particle_min_pt,
            particle_max_abs_eta=particle_max_abs_eta,
            particle_min_num_hits=particle_min_num_hits,
            event_max_num_particles=event_max_num_particles,
        )

        return dataset[0]

    def test_trackml_preprocess(self):
        input_dir = Path("data/trackml/raw/")
        output_dir = Path("data/trackml/prepped")
        output_dir.mkdir(exist_ok=True, parents=True)
        preprocess(input_dir, output_dir, False)

    def test_trackml_event_masks(self, trackml_event):
        _inputs, targets = trackml_event

        particle_valid = targets["particle_valid"]
        particle_hit_mask = targets["particle_hit_valid"]

        # Invalid particle slots should have no hits
        assert torch.all(~particle_hit_mask[~particle_valid.unsqueeze(-1).expand_as(particle_hit_mask)])

    def test_trackml_event_display(self, trackml_event):
        # Quick event display plotted directly from dataloader to verify things look correct
        inputs, targets = trackml_event
        output_dir = Path("tests/outputs/trackml/")
        output_dir.mkdir(exist_ok=True, parents=True)
        fig = plot_trackml_event_reconstruction(inputs, targets)
        fig.savefig(output_dir / "trackml_event.png")

    def test_trackml_matcher(self):
        Matcher(
            default_solver="scipy",
            adaptive_solver=False,
        )
