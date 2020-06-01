import h5py
import numpy as np

import event_model

from suitcase.sas import export


def export_h5_file(output_directory, desc_data_keys, event_page_data_and_timestamps):
    (
        start_doc,
        compose_descriptor,
        compose_resource,
        compose_stop,
    ) = event_model.compose_run(metadata={"md": {"techniques": []}})

    (
        primary_descriptor_doc,
        compose_primary_event,
        compose_primary_event_page,
    ) = compose_descriptor(data_keys=desc_data_keys, name="primary",)

    event_page = compose_primary_event_page(**event_page_data_and_timestamps)

    stop_doc = compose_stop()

    artifacts = export(
        gen=[
            ("start", start_doc),
            ("descriptor", primary_descriptor_doc),
            ("event_page", event_page),
            ("stop", stop_doc),
        ],
        directory=output_directory,
    )

    assert len(artifacts["stream_data"]) == 1
    return artifacts["stream_data"][0]


def test_number_dataset(tmp_path):
    event_page_data_and_timestamps = {
        "seq_num": [1],
        "data": {"en_energy": [270.0012299],},
        "timestamps": {"en_energy": [1573858592.5232499],},
    }
    h5_output_filepath = export_h5_file(
        output_directory=tmp_path,
        desc_data_keys={
            "en_energy": {
                "source": "PY:en_energy.position",
                "dtype": "number",
                "shape": [],
                "upper_ctrl_limit": 2500,
                "lower_ctrl_limit": 150,
                "units": "",
                "object_name": "en",
            },
        },
        event_page_data_and_timestamps=event_page_data_and_timestamps,
    )

    with h5py.File(h5_output_filepath, "r") as h:
        print(list(h["bluesky"]["events"]))
        assert (
            h["bluesky"]["events"]["primary"]["data"]["en_energy"][()]
            == event_page_data_and_timestamps["data"]["en_energy"]
        )
        assert (
            h["bluesky"]["events"]["primary"]["timestamps"]["en_energy"][()]
            == event_page_data_and_timestamps["timestamps"]["en_energy"]
        )


def test_str_dataset(tmp_path):
    event_page_info = {
        "seq_num": [1],
        "data": {"en_monoen_grating_plim_desc": ["Positive End Limit Set"],},
        "timestamps": {"en_monoen_grating_plim_desc": [1573882935.047036],},
    }
    h5_output_filepath = export_h5_file(
        output_directory=tmp_path,
        desc_data_keys={
            "en_monoen_grating_plim_desc": {
                "source": "PV:XF:07ID1-OP{Mono:PGM1-Ax:GrtP}Mtr_PLIM_STS.DESC",
                "dtype": "string",
                "shape": [],
                "units": None,
                "lower_ctrl_limit": None,
                "upper_ctrl_limit": None,
                "object_name": "en",
            },
        },
        event_page_data_and_timestamps=event_page_info,
    )

    with h5py.File(h5_output_filepath, "r") as h:
        h5_events_primary = h["bluesky"]["events"]["primary"]
        assert (
            h5_events_primary["data"]["en_monoen_grating_plim_desc"][()]
            == event_page_info["data"]["en_monoen_grating_plim_desc"]
        )
        assert (
            h5_events_primary["timestamps"]["en_monoen_grating_plim_desc"][()]
            == event_page_info["timestamps"]["en_monoen_grating_plim_desc"]
        )


def test_str_dataset(tmp_path):
    event_page_info = {
        "seq_num": [1],
        "data": {"en_monoen_grating_encoder": [-12189118],},
        "timestamps": {"en_monoen_grating_encoder": [1573882951.510888],},
    }
    h5_output_filepath = export_h5_file(
        output_directory=tmp_path,
        desc_data_keys={
            "en_monoen_grating_encoder": {
                "source": "PV:XF:07ID1-OP{Mono:PGM1-Ax:GrtP}Mtr.REP",
                "dtype": "integer",
                "shape": [],
                "units": "deg",
                "lower_ctrl_limit": -2147483648,
                "upper_ctrl_limit": 2147483647,
                "object_name": "en",
            },
        },
        event_page_data_and_timestamps=event_page_info,
    )

    with h5py.File(h5_output_filepath, "r") as h:
        h5_events_primary = h["bluesky"]["events"]["primary"]
        assert (
            h5_events_primary["data"]["en_monoen_grating_encoder"][()]
            == event_page_info["data"]["en_monoen_grating_encoder"]
        )
        assert (
            h5_events_primary["timestamps"]["en_monoen_grating_encoder"][()]
            == event_page_info["timestamps"]["en_monoen_grating_encoder"]
        )


def test_array_integer_dataset(tmp_path):
    event_page_info = {
        "seq_num": [1],
        "data": {
            "Synced_saxs_image": [
                np.random.randint(
                    low=3000, high=6000, size=(1026, 1024), dtype=np.uint32
                )
            ],
            # 'Synced_saxs_image': array([[5073, 5074, 5082, ..., 5047, 5061, 5051],
            #        [5062, 5089, 5073, ..., 5053, 5043, 5024],
            #        [5080, 5076, 5082, ..., 5037, 5042, 5042],
            #        ...,
            #        [5062, 5053, 5060, ..., 4984, 4987, 4984],
            #        [5054, 5048, 5055, ..., 4981, 4978, 4984],
            #        [5054, 5053, 5043, ..., 4974, 4993, 5008]], dtype=uint32),
        },
        "timestamps": {"Synced_saxs_image": [1573882944.765147],},
    }
    desc_data_keys = {
        "Synced_saxs_image": {
            "shape": [1024, 1026, 0],
            "source": "PV:XF:07ID1-ES:1{GE:1}",
            "dtype": "array",
            "external": "FILESTORE:",
            "object_name": "Synced",
        }
    }

    h5_output_filepath = export_h5_file(
        output_directory=tmp_path,
        desc_data_keys=desc_data_keys,
        event_page_data_and_timestamps=event_page_info,
    )

    with h5py.File(h5_output_filepath, "r") as h:
        h5_events_primary = h["bluesky"]["events"]["primary"]
        assert np.all(
            h5_events_primary["data"]["Synced_saxs_image"][()]
            == event_page_info["data"]["Synced_saxs_image"]
        )
        print(f"what is this: {h5_events_primary['data']['Synced_saxs_image']}")
        # test that dataset shape has been fixed:
        #   the descriptor says the shape is [1024, 1026, 0]
        #   but the array in the event page has shape [1026, 1024]
        #   this is a result of how areadetector reports data shape
        #   and we have to fix it either in the suitcase or using
        #   a transformer
        assert h5_events_primary["data"]["Synced_saxs_image"].shape == (
            1,
            *reversed(desc_data_keys["Synced_saxs_image"]["shape"][:2]),
        )
        assert np.all(
            h5_events_primary["timestamps"]["Synced_saxs_image"][()]
            == event_page_info["timestamps"]["Synced_saxs_image"]
        )
