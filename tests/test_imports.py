def test_imports():
    import faceiq.detector
    import faceiq.exporter
    import faceiq.frame_processor
    import faceiq.image_processor
    import faceiq.media
    import faceiq.quality
    import faceiq.video_processor

    assert faceiq.detector is not None
