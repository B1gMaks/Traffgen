from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from ..core.types import PacketData, Address
from ..common.logger import get_logger


class GraphGenerator:
    """Generate network graphs."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def generate_communication_graph(
        self,
        packets: List[PacketData],
        output_path: Optional[Path] = None,
        max_nodes: int = 30,
        **kwargs
    ) -> Optional[nx.Graph]:
        """Generate communication graph."""
        if not packets:
            self.logger.warning("No packets to visualize")
            return None
        
        graph = nx.Graph()
        edge_weights = {}
        
        for packet in packets:
            src = packet.source.ipv4 or packet.source.mac or "unknown"
            dst = packet.destination.ipv4 or packet.destination.mac or "unknown"
            
            if src == dst:
                continue
            
            # Add nodes
            graph.add_node(src, type='source' if src in [p.source.ipv4 for p in packets[:10]] else 'destination')
            graph.add_node(dst, type='destination')
            
            # Add edge with weight
            edge = tuple(sorted([src, dst]))
            edge_weights[edge] = edge_weights.get(edge, 0) + 1
        
        # Add edges with weights
        for (src, dst), weight in edge_weights.items():
            graph.add_edge(src, dst, weight=weight)
        
        # Limit nodes
        if len(graph.nodes) > max_nodes:
            # Keep nodes with highest degree
            degrees = dict(graph.degree())
            top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:max_nodes]
            graph = graph.subgraph([node for node, _ in top_nodes]).copy()
        
        if output_path:
            self._render_graph(graph, output_path, **kwargs)
        
        return graph
    
    def generate_flow_graph(
        self,
        packets: List[PacketData],
        output_path: Optional[Path] = None,
        **kwargs
    ) -> Optional[nx.DiGraph]:
        """Generate directed flow graph."""
        if not packets:
            self.logger.warning("No packets to visualize")
            return None
        
        graph = nx.DiGraph()
        
        for packet in packets:
            src = packet.source.ipv4 or packet.source.mac or "unknown"
            dst = packet.destination.ipv4 or packet.destination.mac or "unknown"
            
            if src == dst:
                continue
            
            if graph.has_edge(src, dst):
                graph[src][dst]['weight'] += 1
                graph[src][dst]['bytes'] += packet.length
            else:
                graph.add_edge(src, dst, weight=1, bytes=packet.length, protocol=packet.protocol.value)
        
        if output_path:
            self._render_directed_graph(graph, output_path, **kwargs)
        
        return graph
    
    def generate_dependency_graph(
        self,
        packets: List[PacketData],
        output_path: Optional[Path] = None,
        **kwargs
    ) -> Optional[nx.Graph]:
        """Generate host dependency graph."""
        if not packets:
            self.logger.warning("No packets to visualize")
            return None
        
        graph = nx.Graph()
        
        # Track dependencies (client -> server)
        clients = set()
        servers = set()
        
        for packet in packets:
            src = packet.source.ipv4 or packet.source.mac or "unknown"
            dst = packet.destination.ipv4 or packet.destination.mac or "unknown"
            
            if src == dst:
                continue
            
            # Heuristic: if destination port is well-known, it's a server
            if packet.destination.port and packet.destination.port < 1024:
                servers.add(dst)
                clients.add(src)
                graph.add_edge(src, dst, protocol=packet.protocol.value, port=packet.destination.port)
            else:
                clients.add(src)
                servers.add(dst)
                graph.add_edge(src, dst, protocol=packet.protocol.value)
        
        if output_path:
            self._render_graph(graph, output_path, **kwargs)
        
        return graph
    
    def _render_graph(
        self,
        graph: nx.Graph,
        output_path: Path,
        figsize: Tuple[int, int] = (12, 10),
        **kwargs
    ) -> None:
        """Render undirected graph."""
        fig, ax = plt.subplots(figsize=figsize)
        
        pos = nx.spring_layout(graph, k=1, iterations=50)
        
        # Draw nodes
        node_colors = []
        for node in graph.nodes:
            if 'type' in graph.nodes[node]:
                if graph.nodes[node]['type'] == 'source':
                    node_colors.append('lightblue')
                else:
                    node_colors.append('lightgreen')
            else:
                node_colors.append('lightgray')
        
        nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=500, ax=ax)
        
        # Draw edges with weight
        edges = graph.edges()
        weights = [graph[u][v].get('weight', 1) for u, v in edges]
        max_weight = max(weights) if weights else 1
        
        nx.draw_networkx_edges(
            graph, pos,
            width=[w / max_weight * 3 for w in weights],
            alpha=0.6,
            ax=ax
        )
        
        # Draw labels
        nx.draw_networkx_labels(graph, pos, font_size=8, ax=ax)
        
        ax.set_title('Network Communication Graph', fontsize=14, fontweight='bold')
        ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        self.logger.info(f"Saved graph to {output_path}")
    
    def _render_directed_graph(
        self,
        graph: nx.DiGraph,
        output_path: Path,
        figsize: Tuple[int, int] = (12, 10),
        **kwargs
    ) -> None:
        """Render directed graph."""
        fig, ax = plt.subplots(figsize=figsize)
        
        pos = nx.spring_layout(graph, k=1, iterations=50)
        
        # Draw nodes
        nx.draw_networkx_nodes(graph, pos, node_color='lightblue', node_size=500, ax=ax)
        
        # Draw edges with arrows
        edges = graph.edges()
        weights = [graph[u][v].get('weight', 1) for u, v in edges]
        max_weight = max(weights) if weights else 1
        
        nx.draw_networkx_edges(
            graph, pos,
            width=[w / max_weight * 3 for w in weights],
            alpha=0.6,
            arrowstyle='->',
            arrowsize=20,
            ax=ax
        )
        
        # Draw labels
        nx.draw_networkx_labels(graph, pos, font_size=8, ax=ax)
        
        ax.set_title('Traffic Flow Graph', fontsize=14, fontweight='bold')
        ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        self.logger.info(f"Saved directed graph to {output_path}")
