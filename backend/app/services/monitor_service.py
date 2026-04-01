class MonitorService:
    def get_resource_monitor(self, role: str) -> dict:
        data = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0
        }
        if role == "admin":
            data["details"] = {
                "cpu_cores": 4,
                "memory_total": "8GB",
                "disk_total": "100GB"
            }
        return data
    
    def get_service_status(self, role: str) -> dict:
        core_services = {
            "mysql": "running",
            "redis": "running",
            "minio": "running"
        }
        
        if role == "admin":
            all_services = {
                **core_services,
                "elasticsearch": "running",
                "spark": "running",
                "kibana": "running"
            }
            return all_services
        
        return core_services
