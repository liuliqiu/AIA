from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess


def convert_audio(audio_path):
    model_dir = "iic/SenseVoiceSmall"
    model = AutoModel(
        model=model_dir,
        trust_remote_code=True,
        remote_code="./model.py",
        vad_model="fsmn-vad",
        vad_kwargs={"max_single_segment_time": 30000},
        device="cuda",
        disable_update=True,
    )
    res = model.generate(
        input=audio_path,
        cache={},
        language="auto",  # "zn", "en", "yue", "ja", "ko", "nospeech"
        use_itn=True,
        batch_size_s=60,
        merge_vad=True,  #
        merge_length_s=15,
    )
    return rich_transcription_postprocess(res[0]["text"])


if __name__ == "__main__":
    from argparse import ArgumentParser, FileType

    parser = ArgumentParser()
    parser.add_argument("audio_file", type=str)
    parser.add_argument("text", type=str)
    args = parser.parse_args()
    text = convert_audio(args.audio_file)
    with open(args.text, "w") as f:
        f.write(text)
