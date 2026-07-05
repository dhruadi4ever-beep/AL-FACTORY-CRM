package com.aryanlace

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

private data class InventoryUiModel(
    val itemCode: String,
    val produced: String,
    val inProgress: String,
    val finished: String,
    val packed: String,
)

@Composable
fun InventoryScreen() {
    val balances = remember {
        listOf(
            InventoryUiModel("ITM-A", "40", "20", "2000", "1200"),
            InventoryUiModel("ITM-B", "20", "10", "800", "300"),
        )
    }

    var itemCode by remember { mutableStateOf("ITM-A") }
    var adjustment by remember { mutableStateOf("5") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text(text = "Inventory Control & Stock Ledger", style = MaterialTheme.typography.headlineMedium)
        Text(text = "Stage-wise inventory visibility and ledger-backed adjustments")

        Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp)) {
            Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(value = itemCode, onValueChange = { itemCode = it }, label = { Text("Item") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = adjustment, onValueChange = { adjustment = it }, label = { Text("Adjustment") }, modifier = Modifier.fillMaxWidth())
            }
        }

        Text(text = "Balances", style = MaterialTheme.typography.titleMedium)
        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            items(balances) { balance ->
                Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp)) {
                    Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                            Text(text = balance.itemCode, style = MaterialTheme.typography.titleSmall)
                            Text(text = "Produced: ${balance.produced}")
                        }
                        Text(text = "Job work in progress: ${balance.inProgress}")
                        Text(text = "Finished goods: ${balance.finished}")
                        Text(text = "Packed: ${balance.packed}")
                    }
                }
            }
        }
    }
}
