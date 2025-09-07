class Location:
    def __init__(self, location_data: dict):
        self.longitude = location_data.get("longitude")
        self.latitude = location_data.get("latitude")
        self.horizontal_accuracy = location_data.get("horizontal_accuracy")
        self.live_period = location_data.get("live_period")
        self.heading = location_data.get("heading")
        self.proximity_alert_radius = location_data.get("proximity_alert_radius")

    def __str__(self):
        fields = []
        fields.append(f"longitude={self.longitude}")
        fields.append(f"latitude={self.latitude}")
        if self.horizontal_accuracy is not None:
            fields.append(f"horizontal_accuracy={self.horizontal_accuracy}")
        if self.live_period is not None:
            fields.append(f"live_period={self.live_period}")
        if self.heading is not None:
            fields.append(f"heading={self.heading}")
        if self.proximity_alert_radius is not None:
            fields.append(f"proximity_alert_radius={self.proximity_alert_radius}")
        
        return "Location(\n    " + ",\n    ".join(fields) + "\n)"