from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import matplotlib.pyplot as plt
from .charts import ChartGenerator
from .graphs import GraphGenerator
from ..core.types import PacketData
from ..common.logger import get_logger


class Renderer:
    """Unified renderer for all visualizations."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.chart_generator = ChartGenerator()
        self.graph_generator = GraphGenerator()
    
    def render(
        self,
        packets: List[PacketData],
        chart_type: str,
        output_path: Path,
        **kwargs
    ) -> Optional[Union[plt.Figure, nx.Graph]]:
        """Render a specific chart type."""
        chart_types = {
            'pie': self.chart_generator.generate_protocol_pie_chart,
            'histogram': self.chart_generator.generate_packet_size_histogram,
            'timeline': self.chart_generator.generate_timeline_chart,
            'top_talkers': self.chart_generator.generate_top_talkers_bar_chart,
            'heatmap': self.chart_generator.generate_traffic_heatmap,
            'communication': self.graph_generator.generate_communication_graph,
            'flow': self.graph_generator.generate_flow_graph,
            'dependency': self.graph_generator.generate_dependency_graph,
        }
        
        render_func = chart_types.get(chart_type.lower())
        if not render_func:
            self.logger.error(f"Unknown chart type: {chart_type}")
            return None
        
        return render_func(packets, output_path, **kwargs)
    
    def render_all(
        self,
        packets: List[PacketData],
        output_dir: Path,
        **kwargs
    ) -> Dict[str, List[Path]]:
        """Render all charts to a directory."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {
            'charts': [],
            'graphs': [],
        }
        
        # Generate all charts
        chart_files = self.chart_generator.generate_comprehensive_report(packets, output_dir, **kwargs)
        results['charts'].extend(chart_files)
        
        # Generate graphs
        graph_types = [
            ('communication_graph.png', self.graph_generator.generate_communication_graph),
            ('flow_graph.png', self.graph_generator.generate_flow_graph),
            ('dependency_graph.png', self.graph_generator.generate_dependency_graph),
        ]
        
        for filename, graph_func in graph_types:
            output_path = output_dir / filename
            graph = graph_func(packets, output_path, **kwargs)
            if graph:
                results['graphs'].append(output_path)
        
        self.logger.info(f"Rendered all visualizations to {output_dir}")
        return results
