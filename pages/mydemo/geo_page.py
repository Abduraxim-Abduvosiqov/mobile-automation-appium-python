"""Geo Location screen: device latitude and longitude."""
from pages.mydemo.app_page import AppPage, rid


class GeoLocationPage(AppPage):
    TITLE = rid("locationTV")
    LATITUDE = rid("latitudeTV")
    LONGITUDE = rid("longitudeTV")

    def is_opened(self) -> bool:
        return self.is_visible(self.TITLE)

    def latitude(self) -> float:
        return float(self.get_text(self.LATITUDE))

    def longitude(self) -> float:
        return float(self.get_text(self.LONGITUDE))
