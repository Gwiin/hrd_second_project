from firmware.pico2w.sensors import adc_u16_to_lux, adc_u16_to_ppm, adc_u16_to_percent


def test_adc_u16_to_percent_scales_full_range():
    assert adc_u16_to_percent(0) == 0.0
    assert adc_u16_to_percent(65535) == 100.0


def test_adc_u16_to_ppm_scales_to_default_gas_range():
    assert adc_u16_to_ppm(0) == 0
    assert adc_u16_to_ppm(65535) == 1000


def test_adc_u16_to_lux_scales_to_default_light_range():
    assert adc_u16_to_lux(0) == 0
    assert adc_u16_to_lux(65535) == 1000
